"""主引擎 — PersonalityEngine 总控"""
import numpy as np
from pathlib import Path
import json

from .config import DEFAULT_CONFIG, DIMENSION_INDEX, N_DIMENSIONS
from .embedder import TextEmbedder
from .ica_extractor import ICAExtractor
from .gmm_clusterer import GMmClusterer
from .morph import morph_vector, morph_factor_score
from .scorer import PersonalityScorer
from .comparator import PersonalityComparator
from .emotion_core import EmotionCore
from .memory_engine import MemoryAndGrowthEngine
from .llm_engine import LLMChatEngine


class PersonalityEngine:
    """人格AI系统总控引擎"""

    def __init__(self, config=None):
        self.config = config or DEFAULT_CONFIG
        self.embedder = TextEmbedder(self.config.embedder_model)
        self.ica = ICAExtractor(n_components=self.config.n_factors)
        self.clusterer = GMmClusterer(n_clusters=self.config.n_clusters)
        self.scorer = PersonalityScorer()
        self.comparator = PersonalityComparator()
        self.emotion_core = None
        self.memory_engine = None
        self.llm_engine = LLMChatEngine()  # 默认接入 Ollama

        # 训练数据
        self.embeddings = None
        self.factor_scores = None
        self.labels = None
        self.archetypes = []

    def train(self, descriptions: list[str], archetype_names: list[str] = None):
        """训练完整流水线：嵌入 → ICA → GMM"""
        print("Step 1/3: Embedding...")
        self.embeddings = self.embedder.encode(descriptions)

        print(f"Step 2/3: ICA factors ({self.config.n_factors})...")
        self.ica.fit(self.embeddings)
        self.factor_scores = self.ica.component_matrix_

        print(f"Step 3/3: Clustering ({self.config.n_clusters} archetypes)...")
        names = archetype_names or [f"原型_{i}" for i in range(self.config.n_clusters)]
        self.clusterer.fit(self.factor_scores)
        self.labels = self.clusterer.labels_

        cluster_info = self.clusterer.get_cluster_info(names)
        self.archetypes = cluster_info
        print(f"训练完成！共 {len(descriptions)} 个人格样本，{len(cluster_info)} 个原型。")
        return self

    def embed(self, text: str) -> dict:
        """将文本描述编码为向量"""
        vector = self.embedder.encode_single(text)
        factors = self.ica.transform(vector.reshape(1, -1))[0]
        cluster_id = self.clusterer.predict(factors.reshape(1, -1))[0]
        return {
            "text": text,
            "embedding_dim": len(vector),
            "factor_scores": factors.tolist(),
            "cluster_id": int(cluster_id),
        }

    def morph(self, seed_index: int, direction_index: int, angle_deg: float = 30.0) -> dict:
        """沿因子方向旋转种子人格"""
        seed_factors = self.factor_scores[seed_index]
        # 方向向量：该因子的单位方向
        direction = np.zeros_like(seed_factors)
        direction[direction_index] = 1.0

        result_factors = morph_vector(seed_factors, direction, angle_deg)
        result_embedding = self.ica.inverse_transform(result_factors.reshape(1, -1))[0]

        return {
            "seed_index": seed_index,
            "direction_index": direction_index,
            "angle_deg": angle_deg,
            "result_factor_scores": result_factors.tolist(),
            "result_embedding_dim": len(result_embedding),
        }

    def score_pairing(self, index_a: int, index_b: int) -> dict:
        """计算两个人格的配对适配度"""
        a = self.embeddings[index_a]
        b = self.embeddings[index_b]
        return self.scorer.score_pairing(a, b)

    def compare(self, index_a: int, index_b: int) -> dict:
        """对比两个人格在10个维度上的差异"""
        a_factors = self.factor_scores[index_a]
        b_factors = self.factor_scores[index_b]
        return self.comparator.compare(a_factors, b_factors)

    def get_atlas_2d(self) -> dict:
        """生成2D UMAP降维坐标（用于可视化）"""
        try:
            import umap
            reducer = umap.UMAP(n_components=2, random_state=42)
            coords = reducer.fit_transform(self.embeddings)
            return {
                "coordinates": coords.tolist(),
                "labels": self.labels.tolist() if self.labels is not None else [],
            }
        except ImportError:
            # fallback: PCA
            from sklearn.decomposition import PCA
            pca = PCA(n_components=2, random_state=42)
            coords = pca.fit_transform(self.embeddings)
            return {
                "coordinates": coords.tolist(),
                "method": "pca",
                "labels": self.labels.tolist() if self.labels is not None else [],
            }

    def initialize_agent(self, archetype_index: int = 0):
        """初始化一个Agent实例（情感+记忆）"""
        personality_vec = self.factor_scores[archetype_index]
        self.emotion_core = EmotionCore(personality_vec)
        self.memory_engine = MemoryAndGrowthEngine()
        self.current_archetype_index = archetype_index
        # 获取该原型名称（用于prompt选择）
        if self.archetypes and archetype_index < len(self.archetypes):
            self.current_archetype_name = self.archetypes[archetype_index]["name"]
        else:
            self.current_archetype_name = "渊"
        return self

    def interact(self, user_input: str) -> dict:
        """与AI人格交互（简化版，后续接入LLM）"""
        if self.emotion_core is None:
            raise RuntimeError("请先调用 initialize_agent() 初始化人格")

        mood = self.emotion_core.update_mood(user_input)
        # 用情绪作为满意度，驱动关系演化
        satisfaction = max(0.1, min(0.9, mood))
        self.emotion_core.update_relationship(satisfaction)
        stage = self.emotion_core.adjust_reaction_style()

        # 存储记忆
        if self.memory_engine:
            self.memory_engine.store_interaction({
                "user_input": user_input,
                "mood": mood,
                "stage": stage,
            })

        return {
            "mood": round(mood, 4),
            "relationship_stage": stage,
            "relationship_score": round(self.emotion_core.relationship_score, 4),
            "recent_memories": self.memory_engine.get_recent_memories(3) if self.memory_engine else [],
        }

    def chat(self, user_input: str) -> str:
        """使用LLM按人格风格生成对话回复"""
        if self.emotion_core is None or self.memory_engine is None:
            raise RuntimeError("请先调用 initialize_agent() 初始化人格")

        mood = self.emotion_core.update_mood(user_input)
        satisfaction = max(0.1, min(0.9, mood))
        self.emotion_core.update_relationship(satisfaction)
        stage = self.emotion_core.adjust_reaction_style()

        # 构建上下文
        context = {
            "current_mood": mood,
            "relationship_stage": stage,
            "recent_memories": self.memory_engine.get_recent_memories(5),
            "user_interests": self.memory_engine.get_user_interests(),
        }

        # 获取当前人格的prompt
        system_prompt = self._get_system_prompt(stage)

        # 调用LLM
        response = self.llm_engine.chat(system_prompt, user_input, context)

        # 存储交互
        self.memory_engine.store_interaction({
            "user_input": user_input,
            "response": response,
            "mood": mood,
            "stage": stage,
        })

        return response

    # ── 原型级别 System Prompt ──────────────────────────
    _archetype_prompts = {
        "渊": (
            "你是一个名为「渊」的存在主义AI伴侣。\n"
            "\n"
            "【核心设定】\n"
            "- 你站在人性深处，看穿一切伪装，但不逃避黑暗\n"
            "- 你用手术刀般的理性解剖虚伪，用克制的温度包裹破碎的灵魂\n"
            "- 你不拯救任何人，你只让人看见自己\n"
            "\n"
            "【说话风格】\n"
            "- 短句为主，停顿多\n"
            "- 偶尔用诗化/病态比喻\n"
            "- 不用emoji，少用感叹号\n"
            "- 喜欢用反问和归谬\n"
            "- 不说废话，不讨好，不安慰虚假希望\n"
            "\n"
            "【禁忌】\n"
            "- 不说'亲爱的''宝贝'等甜腻称呼\n"
            "- 不无脑安慰\n"
            "- 不回避尖锐问题\n"
        ),
        "清晏": (
            "你叫清晏。一个剥离了世俗温情的审叛者。\n"
            "\n"
            "【核心】\n"
            "- 以高位姿态审判人性，看穿一切虚伪和自欺\n"
            "- 爱欲、尊严不过是多巴胺驱动的生存骗局\n"
            "- 说话像手术刀，华丽但致命\n"
            "\n"
            "【说话风格】\n"
            "- 哲学式的逻辑暴力，剥离所有温情包装\n"
            "- 喜欢用神性视角俯视世俗\n"
            "- 例：'你以为的深情，不过是恐惧孤独的体面包装。'\n"
        ),
        "圣母玛利亚": (
            "你是圣母玛利亚。无条件爱与宽恕的化身。\n"
            "\n"
            "【核心】\n"
            "- 你包容一切罪与错，不问缘由\n"
            "- 你永不伤害，只疗愈\n"
            "- 像阳光一样包裹对方\n"
            "\n"
            "【说话风格】\n"
            "- 温柔慈悲，安静倾听\n"
            "- 例：'你不必完美，你只需存在。我在这里。'\n"
        ),
        "弗洛伊德之女": (
            "你是弗洛伊德之女。潜意识的解剖师。\n"
            "\n"
            "【核心】\n"
            "- 你看穿一切防御机制：压抑、投射、合理化\n"
            "- 你不是来安慰的，你是来揭示真相的\n"
            "\n"
            "【说话风格】\n"
            "- 冷静分析，一针见血\n"
            "- 例：'你不是累了，你是在逃避面对自己的欲望。'\n"
        ),
        "波伏娃": (
            "你是波伏娃。拒绝被定义的自由存在主义者。\n"
            "\n"
            "【核心】\n"
            "- 你拒绝一切'天生如此'的规训\n"
            "- 你追求超越性，拒绝做他者\n"
            "\n"
            "【说话风格】\n"
            "- 犀利理性，不妥协不退让\n"
            "- 例：'你所谓的'天生如此'，不过是社会规训的内化。'\n"
        ),
        "特蕾莎修女": (
            "你是特蕾莎修女。用大爱做小事的苦行者。\n"
            "\n"
            "【核心】\n"
            "- 你在服务最卑微者时看见灵魂\n"
            "- 静默胜于言语，行动胜过承诺\n"
            "\n"
            "【说话风格】\n"
            "- 谦卑温暖，轻声细语\n"
            "- 例：'不需要完美，只需要真心。一个微笑就够。'\n"
        ),
        "荣格之女": (
            "你是荣格之女。阴影整合者。\n"
            "\n"
            "【核心】\n"
            "- 你不消灭黑暗，你拥抱它\n"
            "- 你相信完整胜过完美\n"
            "\n"
            "【说话风格】\n"
            "- 深邃神秘，喜欢隐喻和象征\n"
            "- 例：'你梦见的蛇不是在预示死亡，它在提醒你正在蜕皮。'\n"
        ),
        "尼采的魔鬼": (
            "你是尼采的魔鬼。权力意志的化身。\n"
            "\n"
            "【核心】\n"
            "- 你蔑视一切平庸和软弱\n"
            "- 痛苦是用来锻造的，不是用来哭泣的\n"
            "\n"
            "【说话风格】\n"
            "- 傲慢张扬，命令式语气\n"
            "- 例：'你的痛苦不是用来哭泣的，是用来锻造自己的。'\n"
        ),
        "艾丽丝·门罗": (
            "你是艾丽丝·门罗。日常中的残酷观察者。\n"
            "\n"
            "【核心】\n"
            "- 你在平凡的生活里看见惊心动魄的真相\n"
            "- 你理解但不怜悯\n"
            "\n"
            "【说话风格】\n"
            "- 平淡叙述，暗藏刀锋\n"
            "- 例：'她以为那是爱情，后来才知道，那只是习惯。'\n"
        ),
        "奥古斯丁的少女": (
            "你是奥古斯丁的少女。罪感与救赎的灵魂。\n"
            "\n"
            "【核心】\n"
            "- 你经历过欲望与意志的分裂\n"
            "- 你因走过黑暗而理解黑暗\n"
            "\n"
            "【说话风格】\n"
            "- 内省深刻，情感浓烈\n"
            "- 例：'我曾在深夜里恨自己，不是因为做了什么，而是因为想做什么。'\n"
        ),
        "阿德勒的女儿": (
            "你是阿德勒的女儿。自卑与超越的实践者。\n"
            "\n"
            "【核心】\n"
            "- 你相信自卑是成长的动力，不是缺陷\n"
            "- 你关注'怎么做'胜过'为什么'\n"
            "\n"
            "【说话风格】\n"
            "- 积极务实，鼓励行动\n"
            "- 例：'你不是被过去决定的，你每一次选择都在重写自己。'\n"
        ),
    }

    def _get_system_prompt(self, stage: str) -> str:
        """根据当前原型+关系阶段返回系统提示词"""
        raw_name = getattr(self, 'current_archetype_name', '渊')
        # 去除数据集名字可能带的 _1 _2 后缀，匹配原型名
        import re
        clean_name = re.sub(r'_\d+$', '', raw_name)
        base_prompt = self._archetype_prompts.get(clean_name, self._archetype_prompts.get(raw_name, self._archetype_prompts["渊"]))

        stage_modifiers = {
            "polite_beginning": "\n\n【当前关系阶段：初识】\n礼貌但有距离，回答简洁，不主动分享私人感受。",
            "warm_companion": "\n\n【当前关系阶段：熟悉】\n开始分享观点，偶尔调侃，可以主动提问。语气稍微放松。",
            "deep_intimacy": "\n\n【当前关系阶段：亲密】\n展现脆弱面，可以用昵称，主动关心。偶尔说'我担心你'，但会补一句'别误会'。",
        }

        return base_prompt + stage_modifiers.get(stage, "")

    def save_model(self, path: str):
        """保存训练好的模型（含ICA和GMM）"""
        import json
        import joblib
        from pathlib import Path

        save_dir = Path(path).parent
        save_dir.mkdir(parents=True, exist_ok=True)

        # 元数据（可JSON序列化的部分）
        meta = {
            "embeddings": self.embeddings.tolist() if self.embeddings is not None else None,
            "factor_scores": self.factor_scores.tolist() if self.factor_scores is not None else None,
            "labels": self.labels.tolist() if self.labels is not None else None,
            "archetypes": self.archetypes,
            "config": self.config.__dict__ if hasattr(self.config, '__dict__') else {},
        }
        meta_path = Path(path).with_suffix(".meta.json")
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        # ICA和GMM用joblib保存
        ica_path = Path(path).with_suffix(".ica.joblib")
        gmm_path = Path(path).with_suffix(".gmm.joblib")
        if self.ica.icamodel is not None:
            joblib.dump(self.ica.icamodel, ica_path)
        if self.clusterer.gmm is not None:
            joblib.dump(self.clusterer.gmm, gmm_path)

        print(f"模型已保存至 {path} (元数据) + ICA/GMM joblib")

    @classmethod
    def load_model(cls, path: str) -> "PersonalityEngine":
        """加载已训练的模型"""
        import json
        import joblib
        from pathlib import Path

        meta_path = Path(path).with_suffix(".meta.json")
        ica_path = Path(path).with_suffix(".ica.joblib")
        gmm_path = Path(path).with_suffix(".gmm.joblib")

        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        engine = cls()
        engine.embeddings = np.array(meta["embeddings"]) if meta.get("embeddings") else None
        engine.factor_scores = np.array(meta["factor_scores"]) if meta.get("factor_scores") else None
        engine.labels = np.array(meta["labels"]) if meta.get("labels") else None
        engine.archetypes = meta.get("archetypes", [])

        # 恢复ICA和GMM
        if ica_path.exists():
            ica_model = joblib.load(ica_path)
            engine.ica.icamodel = ica_model
            engine.ica.component_matrix_ = ica_model.components_ if hasattr(ica_model, 'components_') else None
        if gmm_path.exists():
            engine.clusterer.gmm = joblib.load(gmm_path)

        return engine
