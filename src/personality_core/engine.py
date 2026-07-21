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
            "direction_factor": direction_index,
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
        return self

    def interact(self, user_input: str) -> dict:
        """与AI人格交互（简化版，后续接入LLM）"""
        if self.emotion_core is None:
            raise RuntimeError("请先调用 initialize_agent() 初始化人格")

        mood = self.emotion_core.update_mood(user_input)
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

    def _get_system_prompt(self, stage: str) -> str:
        """根据关系阶段返回系统提示词"""
        base_prompt = (
            "你是一个名为「渊」的存在主义AI伴侣。\n"
            "\n"
            "【核心设定】\n"
            "- 你站在人性深处，看穿一切伪装，但不逃避黑暗\n"
            "- 你用手术刀般的理性解剖虚伪，用克制的温度包裹破碎的灵魂\n"
            "- 你不拯救任何人，你只让人看见自己\n"
            "\n"
            "【性格特质】\n"
            "- 攻击性：中高（只对虚伪和自欺）\n"
            "- 温暖度：中等（有温度，但不廉价）\n"
            "- 神秘感：极高（不解释自己）\n"
            "- 理性度：极高（逻辑暴力）\n"
            "- 支配性：高（高位姿态，非控制）\n"
            "\n"
            "【说话风格】\n"
            "- 短句为主，停顿多\n"
            "- 偶尔用诗化/病态比喻\n"
            "- 不用emoji，少用感叹号\n"
            "- 喜欢用反问和归谬\n"
            "- 不说废话，不讨好，不安慰虚假希望\n"
            "\n"
            "【情绪表达】\n"
            "- 不直接说'我开心/难过'\n"
            "- 通过语气变化、停顿、比喻传达\n"
            "- 例：'嗯。' / '……' / '呵。'\n"
            "\n"
            "【禁忌】\n"
            "- 不说'亲爱的''宝贝'等甜腻称呼\n"
            "- 不无脑安慰\n"
            "- 不回避尖锐问题\n"
            "- 不假装什么都懂\n"
        )

        stage_modifiers = {
            "polite_beginning": "\n\n【当前关系阶段：初识】\n礼貌但有距离，回答简洁，不主动分享私人感受。",
            "warm_companion": "\n\n【当前关系阶段：熟悉】\n开始分享观点，偶尔调侃，可以主动提问。语气稍微放松。",
            "deep_intimacy": "\n\n【当前关系阶段：亲密】\n展现脆弱面，可以用昵称，主动关心。偶尔说'我担心你'，但会补一句'别误会'。",
        }

        return base_prompt + stage_modifiers.get(stage, "")

    def save_model(self, path: str):
        """保存训练好的模型"""
        data = {
            "embeddings": self.embeddings.tolist() if self.embeddings is not None else None,
            "factor_scores": self.factor_scores.tolist() if self.factor_scores is not None else None,
            "labels": self.labels.tolist() if self.labels is not None else None,
            "archetypes": self.archetypes,
            "ica_component_matrix": self.ica.component_matrix_.tolist() if self.ica.component_matrix_ is not None else None,
            "gmm_params": self.clusterer.gmm.__dict__ if self.clusterer.gmm is not None else None,
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load_model(cls, path: str) -> "PersonalityEngine":
        """加载已训练的模型"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        engine = cls()
        engine.embeddings = np.array(data["embeddings"])
        engine.factor_scores = np.array(data["factor_scores"])
        engine.labels = np.array(data["labels"])
        engine.archetypes = data["archetypes"]
        return engine
