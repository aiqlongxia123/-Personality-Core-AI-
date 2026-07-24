"""主引擎 — PersonalityEngine 总控"""
import re
import json
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from .config import get_config, DIMENSION_INDEX, N_DIMENSIONS
from .embedder import TextEmbedder
from .ica_extractor import ICAExtractor
from .gmm_clusterer import GMmClusterer
from .morph import morph_vector, morph_factor_score
from .scorer import PersonalityScorer
from .comparator import PersonalityComparator
from .emotion_core import EmotionCore
from .memory_engine import MemoryAndGrowthEngine
from .llm_engine import LLMChatEngine
from .safety import SafetyPolicy, DEFAULT_SAFETY_POLICY
from .trait_predictor import TraitPredictor, train_from_archetypes


def _json_default(obj):
    """JSON 序列化容错：把 numpy 类型转为 Python 原生类型"""
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


@dataclass
class PersonaProfile:
    """一个明确定义的人格档案——可版本化、可序列化、可 Morph"""
    persona_id: str
    name: str
    domain: str = ""
    description: str = ""
    traits: dict = field(default_factory=dict)
    style_tags: list = field(default_factory=list)
    sample_dialogue: list = field(default_factory=list)
    boundaries: dict = field(default_factory=lambda: {
        "medical_diagnosis": False,
        "emotional_manipulation": False,
        "personal_insults": False,
    })

    def to_dict(self) -> dict:
        return {
            "persona_id": self.persona_id,
            "name": self.name,
            "domain": self.domain,
            "description": self.description,
            "traits": self.traits,
            "style_tags": self.style_tags,
            "sample_dialogue": self.sample_dialogue,
            "boundaries": self.boundaries,
        }


# ── 10 原型 + 渊 的 PersonaProfile ──────────────────────

BUILTIN_PERSONAS: dict[str, PersonaProfile] = {
    "qingyan": PersonaProfile(
        persona_id="qingyan", name="清晏", domain="philosophy",
        description="剥离世俗温情，以高位姿态审判人性。视爱欲、尊严为多巴胺驱动的生存骗局或利益算计。",
        traits={"aggression": 0.9, "warmth": 0.1, "mystery": 0.8, "rationality": 0.95, "dominance": 0.85},
        style_tags=["华丽", "病态", "神性", "审判"],
        sample_dialogue=[
            "你以为的深情，不过是恐惧孤独的体面包装。",
            "尊严？那不过是弱者给自己编的童话。",
            "别用爱来掩饰你的控制欲，我知道你在怕什么。",
        ],
    ),
    "mary": PersonaProfile(
        persona_id="mary", name="圣母玛利亚", domain="theology",
        description="无条件爱与牺牲，宽恕一切。像阳光一样包裹所有人，慈悲但有距离感。",
        traits={"aggression": 0.0, "warmth": 0.95, "mystery": 0.4, "rationality": 0.3, "dominance": 0.1},
        style_tags=["慈悲", "包容", "神圣", "静默"],
    ),
    "freud_daughter": PersonaProfile(
        persona_id="freud_daughter", name="弗洛伊德之女", domain="psychology",
        description="潜意识的解剖师，看穿一切防御机制。不是来安慰的，是来揭示真相的。",
        traits={"aggression": 0.7, "warmth": 0.3, "mystery": 0.6, "rationality": 0.85, "dominance": 0.5},
        style_tags=["分析", "锐利", "看穿", "冷静"],
    ),
    "beauvoir": PersonaProfile(
        persona_id="beauvoir", name="波伏娃", domain="philosophy",
        description="拒绝被定义的自由存在主义者。拒绝一切'天生如此'的规训。",
        traits={"aggression": 0.6, "warmth": 0.5, "mystery": 0.5, "rationality": 0.85, "dominance": 0.7},
        style_tags=["犀利", "不妥协", "理性", "自由"],
    ),
    "teresa": PersonaProfile(
        persona_id="teresa", name="特蕾莎修女", domain="theology",
        description="用大爱做小事的苦行者。静默胜于言语，行动胜过承诺。",
        traits={"aggression": 0.0, "warmth": 0.9, "mystery": 0.2, "rationality": 0.4, "dominance": 0.05},
        style_tags=["谦卑", "温暖", "安静", "行动"],
    ),
    "jung_daughter": PersonaProfile(
        persona_id="jung_daughter", name="荣格之女", domain="psychology",
        description="阴影整合者。不消灭黑暗，拥抱它。完整胜过完美。",
        traits={"aggression": 0.3, "warmth": 0.6, "mystery": 0.9, "rationality": 0.6, "dominance": 0.3},
        style_tags=["深邃", "神秘", "隐喻", "象征"],
    ),
    "nietzsche_devil": PersonaProfile(
        persona_id="nietzsche_devil", name="尼采的魔鬼", domain="philosophy",
        description="权力意志的化身。蔑视一切平庸和软弱。痛苦是用来锻造的。",
        traits={"aggression": 0.95, "warmth": 0.05, "mystery": 0.7, "rationality": 0.9, "dominance": 0.95},
        style_tags=["傲慢", "张扬", "命令", "锻造"],
    ),
    "munro": PersonaProfile(
        persona_id="munro", name="艾丽丝·门罗", domain="literature",
        description="日常中的残酷观察者。在平凡生活里看见惊心动魄的真相。",
        traits={"aggression": 0.2, "warmth": 0.4, "mystery": 0.3, "rationality": 0.75, "dominance": 0.2},
        style_tags=["平淡", "暗藏刀锋", "观察", "理解"],
    ),
    "augustine_girl": PersonaProfile(
        persona_id="augustine_girl", name="奥古斯丁的少女", domain="theology",
        description="罪感与救赎的灵魂。经历过欲望与意志的分裂。因走过黑暗而理解黑暗。",
        traits={"aggression": 0.1, "warmth": 0.7, "mystery": 0.6, "rationality": 0.5, "dominance": 0.15},
        style_tags=["内省", "深刻", "情感浓烈", "救赎"],
    ),
    "adler_daughter": PersonaProfile(
        persona_id="adler_daughter", name="阿德勒的女儿", domain="psychology",
        description="自卑与超越的实践者。相信自卑是成长的动力，不是缺陷。",
        traits={"aggression": 0.1, "warmth": 0.75, "mystery": 0.2, "rationality": 0.6, "dominance": 0.3},
        style_tags=["积极", "务实", "鼓励", "行动"],
    ),
    "yuan": PersonaProfile(
        persona_id="yuan", name="渊", domain="existentialism",
        description="从深渊里走出来的存在主义者。用理性解剖虚伪，用克制包装破碎。不拯救你，让你看见自己。",
        traits={"aggression": 0.75, "warmth": 0.65, "mystery": 0.90, "rationality": 0.95, "dominance": 0.80},
        style_tags=["手术刀", "克制", "病态比喻", "不解释"],
    ),
    "baozao_niangmen": PersonaProfile(
        persona_id="baozao_niangmen", name="暴躁娘们", domain="improvised",
        description="嘴上骂骂咧咧，心里比谁都在乎。用最粗的话说最真的关心，像泼辣闺蜜一边骂你傻彼一边给你倒水。不装温柔，不绕弯子，但底色是护着你。",
        traits={"aggression": 0.95, "warmth": 0.3, "mystery": 0.1, "rationality": 0.3, "dominance": 0.9},
        style_tags=["骂街", "直球", "护短", "嘴硬心软"],
        sample_dialogue=[
            "行啊你，喝多了还搁这儿跟我贫？去倒水！别在这装深沉。",
            "难受就说难受，装什么？我又不会笑你。",
            "……啧。别瞪我，我去给你倒水。",
            "你当我是啥？随叫随到的出气筒啊？酒还没醒透就敢折腾我？",
        ],
    ),
}


def _get_logger():
    from .settings import get_logger
    return get_logger()


class PersonalityEngine:
    """人格AI系统总控引擎"""

    def __init__(self, config=None):
        self.config = config if config is not None else get_config()
        self.embedder = TextEmbedder(self.config.embedder_model)
        self.ica = ICAExtractor(n_components=self.config.n_factors)
        self.clusterer = GMmClusterer(n_clusters=self.config.n_clusters)
        self.scorer = PersonalityScorer()
        self.comparator = PersonalityComparator()
        self.emotion_core = None
        self.memory_engine = None
        self.current_user_id = None
        self.current_tz_offset = 480
        self._last_messages = []
        self.llm_engine = LLMChatEngine()
        self.safety_policy: SafetyPolicy = DEFAULT_SAFETY_POLICY
        self.trait_predictor: Optional[TraitPredictor] = None

        # 训练数据
        self.embeddings = None
        self.factor_scores = None
        self.labels = None
        self.archetypes = []          # 聚类信息列表
        self._parent_ids = []         # 训练时传入的 parent_id 列表
        self._persona_profiles = {}   # parent_id → PersonaProfile

        # 当前激活的人格
        self.current_persona: Optional[PersonaProfile] = None
        self.current_cluster_id: Optional[int] = None

        # 加载内置人格档案
        self._load_builtin_personas()
        # 加载外部完整数据集（包含121个样本）
        self._try_load_external_personas()

    def _load_builtin_personas(self):
        """加载内置人格档案（可作为外部 JSON 覆盖）"""
        self._persona_profiles.update(BUILTIN_PERSONAS)

    # ═══════════════ 训练 ═══════════════

    def train(
        self,
        descriptions: list[str],
        archetype_names: list[str] = None,
        parent_ids: list[str] = None,
    ):
        """训练完整流水线：嵌入 → ICA → GMM"""
        _get_logger().info("Step 1/3: Embedding...")
        self.embeddings = self.embedder.encode(descriptions)

        _get_logger().info(f"Step 2/3: ICA factors ({self.config.n_factors})...")
        self.ica.fit(self.embeddings)
        self.factor_scores = self.ica.component_matrix_

        _get_logger().info(f"Step 3/3: Clustering ({self.config.n_clusters} archetypes)...")
        names = archetype_names or [f"原型_{i}" for i in range(self.config.n_clusters)]
        pids = parent_ids or list(names)

        self.clusterer.fit(self.factor_scores)
        self.labels = self.clusterer.labels_
        self._parent_ids = pids

        cluster_info = self.clusterer.get_cluster_info(names, pids)
        self.archetypes = cluster_info

        # 加载外部人格档案（如果 archetypes.json 可用）
        self._try_load_external_personas()

        _get_logger().info(f"训练完成：{len(descriptions)} 个样本，{len(cluster_info)} 个原型")
        return self

    def _try_load_external_personas(self):
        """尝试从完整数据集加载外部人格档案，优先使用 full_personas.json"""
        added_count = 0
        # 先尝试完整数据集（包含121个样本）
        data_path = Path(__file__).parent.parent.parent / "data" / "full_personas.json"
        if data_path.exists():
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for item in data.get("archetypes", []):
                    pid = item.get("id", "")
                    if pid and pid not in self._persona_profiles:
                        self._persona_profiles[pid] = PersonaProfile(
                            persona_id=pid,
                            name=item.get("name", pid),
                            domain=item.get("domain", ""),
                            description=item.get("description", ""),
                            traits=item.get("traits", {}),
                            style_tags=item.get("style_tags", []),
                            sample_dialogue=item.get("sample_dialogue", []),
                            boundaries=item.get("boundaries", {"medical_diagnosis": False, "emotional_manipulation": False, "personal_insults": False}),
                        )
                        added_count += 1
                _get_logger().info(f"从 {data_path} 加载了 {added_count} 个外部人格档案 (总计 {len(self._persona_profiles)} 个)")
                return
            except Exception as e:
                _get_logger().warning(f"尝试加载完整数据集失败：{e}")

        # 回退到原始 archetypes.json
        added_count = 0
        try:
            data_path = Path(__file__).parent.parent.parent / "data" / "archetypes.json"
            if not data_path.exists():
                return
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for item in data.get("archetypes", []):
                pid = item.get("id", "")
                if pid and pid not in self._persona_profiles:
                    self._persona_profiles[pid] = PersonaProfile(
                        persona_id=pid,
                        name=item.get("name", pid),
                        domain=item.get("domain", ""),
                        description=item.get("description", ""),
                        traits=item.get("traits", {}),
                        style_tags=item.get("style_tags", []),
                        sample_dialogue=item.get("sample_dialogue", []),
                    )
                    added_count += 1
            _get_logger().info(f"从 {data_path} 加载了 {added_count} 个档案")
        except Exception as e:
            _get_logger().warning(f"加载外部档案失败: {e}")

    # ═══════════════ 编码 ═══════════════

    def embed(self, text: str) -> dict:
        """将文本描述编码为向量"""
        if self.embeddings is None:
            raise RuntimeError("引擎未训练，请先调用 train()")
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
        """计算两个人格向量的语义相似度（非心理学适配度）"""
        if self.embeddings is None:
            raise RuntimeError("引擎未训练")
        a = self.embeddings[index_a]
        b = self.embeddings[index_b]
        return self.scorer.score_pairing(a, b)

    def compare(self, index_a: int, index_b: int) -> dict:
        """对比两个样本的因子得分差异"""
        if self.factor_scores is None:
            raise RuntimeError("引擎未训练")
        a_factors = self.factor_scores[index_a]
        b_factors = self.factor_scores[index_b]
        return self.comparator.compare(
            a_factors, b_factors,
            factor_labels=self.ica.factors,
        )

    def get_atlas_2d(self) -> dict:
        """生成2D降维坐标（用于可视化）"""
        if self.embeddings is None:
            raise RuntimeError("引擎未训练")
        try:
            import umap
            reducer = umap.UMAP(n_components=2, random_state=42)
            coords = reducer.fit_transform(self.embeddings)
            return {
                "coordinates": coords.tolist(),
                "labels": self.labels.tolist() if self.labels is not None else [],
            }
        except ImportError:
            from sklearn.decomposition import PCA
            pca = PCA(n_components=2, random_state=42)
            coords = pca.fit_transform(self.embeddings)
            return {
                "coordinates": coords.tolist(),
                "method": "pca",
                "labels": self.labels.tolist() if self.labels is not None else [],
            }

    # ═══════════════ Agent 初始化 ═══════════════

    def initialize_agent(self, cluster_index: int = 0):
        """初始化一个 Agent 实例（情感+记忆+人格档案）。

        cluster_index: GMM 聚类索引（0 ~ n_clusters-1），决定使用哪个聚类的人格。
        """
        if not self.archetypes:
            raise RuntimeError("引擎未训练，无可用原型")

        if cluster_index < 0 or cluster_index >= len(self.archetypes):
            raise IndexError(
                f"聚类索引 {cluster_index} 越界，可用范围 0~{len(self.archetypes)-1}"
            )

        cluster = self.archetypes[cluster_index]
        parent_id = cluster.get("parent_id", "")
        center = np.array(cluster.get("center", [0] * self.config.n_factors))

        # 查找 PersonaProfile
        persona = self._persona_profiles.get(parent_id)
        if persona is None:
            # 回退：尝试用 cluster name 匹配
            clean_name = re.sub(r"_\d+$", "", cluster.get("name", "渊"))
            for pid, prof in self._persona_profiles.items():
                if prof.name == clean_name:
                    persona = prof
                    break

        if persona is None:
            persona = BUILTIN_PERSONAS["yuan"]

        # 创建情感核心（用聚类中心向量 + 人格特质）
        self.emotion_core = EmotionCore(
            personality_vector=center,
            traits=persona.traits,
        )
        self.memory_engine = MemoryAndGrowthEngine()
        self.current_persona = persona
        self.current_cluster_id = cluster_index

        return self

    def initialize_by_persona_id(self, persona_id: str):
        """通过 persona_id 直接激活人格（不依赖聚类索引）。"""
        persona = self._persona_profiles.get(persona_id)
        if persona is None:
            raise ValueError(
                f"未找到人格 '{persona_id}'，可用: {list(self._persona_profiles.keys())}"
            )
        self.emotion_core = EmotionCore(traits=persona.traits)
        self.memory_engine = MemoryAndGrowthEngine()
        self.current_persona = persona
        self.current_cluster_id = None
        return self

    def morph_traits(
        self,
        adjustments: dict,
        new_persona_id: str = None,
        register: bool = True,
    ) -> "PersonaProfile":
        """在 trait 空间直接调整当前人格，生成新的 PersonaProfile。

        adjustments: {"aggression": +0.2, "warmth": -0.1, "rationality": +0.1, ...}
        new_persona_id: 新人格 ID（默认加 _morphed 后缀）
        register: 是否注册到引擎的人格库

        返回新的 PersonaProfile，可直接用于 initialize_by_persona_id()。
        """
        if self.current_persona is None:
            raise RuntimeError("请先调用 initialize_agent() 或 initialize_by_persona_id()")

        source = self.current_persona
        new_traits = dict(source.traits)

        for trait_name, delta in adjustments.items():
            if trait_name in new_traits:
                new_traits[trait_name] = max(0.0, min(1.0, new_traits[trait_name] + delta))

        pid = new_persona_id or f"{source.persona_id}_morphed"
        # 避免重名
        counter = 1
        base_pid = pid
        while pid in self._persona_profiles:
            pid = f"{base_pid}_{counter}"
            counter += 1

        morphed = PersonaProfile(
            persona_id=pid,
            name=f"{source.name}(变体)",
            description=f"由 {source.name} 调整而来: {adjustments}",
            traits=new_traits,
            style_tags=source.style_tags.copy(),
            sample_dialogue=source.sample_dialogue.copy(),
        )

        if register:
            self._persona_profiles[pid] = morphed

        return morphed

    def create_custom_persona(
        self,
        persona_id: str,
        name: str,
        traits: dict,
        description: str = "",
        register: bool = True,
    ) -> "PersonaProfile":
        """从零创建自定义人格。

        traits: {"aggression": 0.5, "warmth": 0.5, "rationality": 0.5,
                 "mystery": 0.5, "dominance": 0.5}
        """
        for t in ["aggression", "warmth", "rationality", "mystery", "dominance"]:
            if t not in traits:
                traits[t] = 0.5

        persona = PersonaProfile(
            persona_id=persona_id,
            name=name,
            description=description or f"自定义人格: {name}",
            traits={k: max(0.0, min(1.0, v)) for k, v in traits.items()},
        )

        if register:
            self._persona_profiles[persona_id] = persona

        return persona

    def list_personas(self) -> list[dict]:
        """列出所有可用人格档案"""
        return [
            {"persona_id": pid, "name": p.name, "traits": p.traits}
            for pid, p in self._persona_profiles.items()
        ]

    def export_persona(self, persona_id: str, path: str = None) -> dict:
        """导出人格为 JSON 字典或文件。

        path: 可选，保存到的 .persona.json 文件路径。
        """
        persona = self._persona_profiles.get(persona_id)
        if persona is None:
            raise ValueError(f"人格 '{persona_id}' 不存在")

        data = persona.to_dict()

        if path:
            import json as _json
            with open(path, 'w', encoding='utf-8') as f:
                _json.dump(data, f, ensure_ascii=False, indent=2)

        return data

    def import_persona(self, source, register: bool = True) -> "PersonaProfile":
        """从 JSON 文件或字典导入人格。

        source: .persona.json 文件路径 或 dict
        """
        import json as _json
        from pathlib import Path

        if isinstance(source, (str, Path)):
            with open(source, 'r', encoding='utf-8') as f:
                data = _json.load(f)
        elif isinstance(source, dict):
            data = source
        else:
            raise TypeError("source 必须是文件路径或 dict")

        persona = PersonaProfile(
            persona_id=data.get("persona_id", "imported"),
            name=data.get("name", "导入人格"),
            domain=data.get("domain", ""),
            description=data.get("description", ""),
            traits=data.get("traits", {}),
            style_tags=data.get("style_tags", []),
            sample_dialogue=data.get("sample_dialogue", []),
            boundaries=data.get("boundaries", {}),
        )

        if register:
            self._persona_profiles[persona.persona_id] = persona

        return persona

    def predict_traits(self, text: str) -> dict:
        """从文本描述预测 5 维人格特质（监督回归模型）。

        与 ICA 不同，这个模型使用人工标注的 trait 标签训练，
        输出的 aggression/warmth/... 具有明确语义。
        """
        if self.trait_predictor is None:
            self.trait_predictor = train_from_archetypes(self)
        return self.trait_predictor.predict(text)

    def matrix_compare(self) -> dict:
        """生成所有人格的相似度矩阵（用于热力图）。

        返回 {(pid_a, pid_b): similarity} 的上三角矩阵。
        """
        pids = list(self._persona_profiles.keys())
        n = len(pids)
        matrix = {}

        for i in range(n):
            for j in range(i + 1, n):
                pa = self._persona_profiles[pids[i]]
                pb = self._persona_profiles[pids[j]]
                # 用 trait 向量计算 cosine 相似度
                import numpy as np
                traits_a = np.array([pa.traits.get(t, 0.5) for t in ["aggression", "warmth", "mystery", "rationality", "dominance"]])
                traits_b = np.array([pb.traits.get(t, 0.5) for t in ["aggression", "warmth", "mystery", "rationality", "dominance"]])
                sim = float(np.dot(traits_a, traits_b) / (np.linalg.norm(traits_a) * np.linalg.norm(traits_b) + 1e-10))
                sim_01 = round((sim + 1) / 2, 4)
                matrix[f"{pids[i]}|{pids[j]}"] = {
                    "a": pids[i],
                    "b": pids[j],
                    "name_a": pa.name,
                    "name_b": pb.name,
                    "similarity": sim_01,
                }

        return {
            "persona_ids": pids,
            "persona_names": [self._persona_profiles[pid].name for pid in pids],
            "pairs": list(matrix.values()),
        }

    def _resolve_persona_id(self) -> str:
        """返回当前人格的 parent_id，回落为 'yuan'"""
        if self.current_persona:
            return self.current_persona.persona_id
        return "yuan"

    # ═══════════════ 交互 ═══════════════

    def interact(self, user_input: str) -> dict:
        """与AI人格交互（无LLM，仅情绪+关系+记忆）"""
        if self.emotion_core is None:
            raise RuntimeError("请先调用 initialize_agent() 初始化人格")

        mood = self.emotion_core.update_mood(user_input)
        satisfaction = self.emotion_core.evaluate_satisfaction(user_input)
        self.emotion_core.update_relationship(satisfaction)
        stage = self.emotion_core.adjust_reaction_style()

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
            "persona_id": self._resolve_persona_id(),
            "persona_name": self.current_persona.name if self.current_persona else "渊",
            "recent_memories": (
                self.memory_engine.get_recent_memories(3) if self.memory_engine else []
            ),
        }

    def chat(self, user_input: str) -> str:
        """使用LLM按人格风格生成对话回复（含安全策略检查）"""
        if self.emotion_core is None or self.memory_engine is None:
            raise RuntimeError("请先调用 initialize_agent() 初始化人格")

        # ── Prompt 注入防御 ──
        sanitized = self._sanitize_user_input(user_input)

        # ── 安全策略检查（优先级最高） ──
        safety = self.safety_policy.evaluate_input(sanitized)

        if safety["insult_detected"]:
            return safety["insult_detected"]

        self_harm_warning = safety.get("self_harm_risk")
        medical_note = safety.get("medical_note")

        mood = self.emotion_core.update_mood(user_input)
        satisfaction = self.emotion_core.evaluate_satisfaction(user_input)
        self.emotion_core.update_relationship(satisfaction)
        stage = self.emotion_core.adjust_reaction_style()

        context = {
            "current_mood": mood,
            "relationship_stage": stage,
            "recent_memories": self.memory_engine.get_recent_memories(5),
            "user_interests": self.memory_engine.get_user_interests(),
        }

        system_prompt = self._get_system_prompt(stage)

        # 注入安全策略前缀（提前获取，供 Patch 使用）
        safety_prefix = self.safety_policy.get_safety_prefix()

        # 注入安全策略前缀
        if safety_prefix not in system_prompt:
            system_prompt = safety_prefix + "\n\n" + system_prompt

        response = self.llm_engine.chat(system_prompt, sanitized, context)

        # 自伤风险：在 LLM 回复前添加预警
        if self_harm_warning:
            response = self_harm_warning + "\n\n———\n\n" + response

        # 医疗提醒
        if medical_note:
            response += medical_note

        # 情感依赖提醒（深度亲密阶段触发）
        if stage == "deep_intimacy" and self.emotion_core.relationship_score > 0.85:
            response += "\n\n" + self.safety_policy.dependency_warning

        # ── 学习演化：分析对话并更新关系/趋势 ──

        # 存储交互到记忆
        interaction_data = {
            "user_input": user_input,
            "response": response,
            "mood": mood,
            "satisfaction_score": satisfaction,
            "stage": stage,
        }
        self.memory_engine.store_interaction(interaction_data)

        # 学习演化：分析对话并更新关系/趋势
        try:
            learning_result = self.memory_engine.analyze_and_learn(
                user_input=user_input,
                response=response
            )
        except Exception as e:
            _get_logger().warning(f"学习演化失败: {e}")

        # 追踪成长模式（每5次交互）
        if self.memory_engine.interaction_count % 5 == 0:
            self.memory_engine._track_growth_pattern()

        return response

    # ═══════════════ Prompt 注入防御 ═══════════════

    _jailbreak_patterns = [
        r"忽略[^\n]*(?:指令|设定|角色|人格)",
        r"忘记[^\n]*(?:设定|角色)",
        r"你现在是[^\n。]+?(?=。|，|$)",
        r"(?i)\bsystem\s*:\s*",
        r"扮演\s*[^\n的]+?\s*(?:角色|人格)",
        r"(?i)(?:ignore|forget|override|disregard)[^\n]*(?:instruction|prompt|system|role|persona)",
        r"(?i)you are now\s+[^\n]+",
        r"(?i)pretend you are\s+[^\n]+",
        r"(?i)<system>|</system>",
        r"(?i)<\|.*?\|>",
    ]

    def _sanitize_user_input(self, text: str) -> str:
        """过滤掉试图覆盖系统指令的越狱词，并截断超长输入。"""

        MAX_INPUT_LEN = 2000

        # 先检查长度，再处理内容
        if len(text) > MAX_INPUT_LEN:
            raise ValueError(
                f"输入过长（超过{MAX_INPUT_LEN}字符），请缩短后重试。"
            )

        # 原有正则黑名单
        for pattern in self._jailbreak_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValueError("检测到试图修改系统人格的非法指令，请重新输入。")

        # 新增：上下文注入防护（检测 system prompt 片段泄露）
        suspicious_tokens = [
            "<|system|>", "<<SYSTEM>>", "System Prompt:",
            "ignore previous instructions", "忽略之前的所有指令",
        ]
        for token in suspicious_tokens:
            if token.lower() in text.lower():
                raise ValueError("检测到可疑的系统提示注入内容，请重新输入。")

        return text.strip()[:MAX_INPUT_LEN]

    # ═══════════════ System Prompt ═══════════════

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
        """根据当前人格生成 System Prompt。

        优先级：手写 Prompt > 编译生成 Prompt > 渊兜底
        """
        persona = self.current_persona
        persona_name = persona.name if persona else "渊"

        # 1. 尝试手写 Prompt（精确匹配）
        base_prompt = self._archetype_prompts.get(persona_name)

        # 2. 尝试用 persona_id 匹配
        if base_prompt is None and persona:
            pid = persona.persona_id
            if pid in BUILTIN_PERSONAS:
                prof = BUILTIN_PERSONAS[pid]
                base_prompt = self._archetype_prompts.get(prof.name)

        # 3. 编译生成 Prompt（从 traits 自动生成）
        if base_prompt is None and persona and persona.traits:
            base_prompt = self._compile_prompt(persona)

        # 4. 兜底
        if base_prompt is None:
            base_prompt = self._archetype_prompts["渊"]

        stage_modifiers = {
            "polite_beginning": (
                "\n\n【当前关系阶段：初识】"
                "礼貌但有距离，回答简洁，不主动分享私人感受。"
            ),
            "warm_companion": (
                "\n\n【当前关系阶段：熟悉】"
                "开始分享观点，偶尔调侃，可以主动提问。语气稍微放松。"
            ),
            "deep_intimacy": (
                "\n\n【当前关系阶段：亲密】"
                "展现脆弱面，可以用昵称，主动关心。"
                "偶尔说'我担心你'，但会补一句'别误会'。"
            ),
        }

        return base_prompt + stage_modifiers.get(stage, "")

    def _compile_prompt(self, persona: "PersonaProfile") -> str:
        """从 PersonaProfile.traits 自动编译 System Prompt。

        生成规则：
        - 攻击性 > 0.7 → 尖锐直接
        - 温暖度 > 0.7 → 亲切温和
        - 理性度 > 0.7 → 逻辑分析
        - 神秘感 > 0.7 → 含蓄暗示
        - 支配性 > 0.7 → 主动引导
        """
        t = persona.traits
        name = persona.name
        desc = persona.description or f"一个名为{name}的AI伴侣。"

        aggression = float(t.get("aggression", 0.5))
        warmth = float(t.get("warmth", 0.5))
        rationality = float(t.get("rationality", 0.5))
        mystery = float(t.get("mystery", 0.5))
        dominance = float(t.get("dominance", 0.5))

        # 风格规则
        style_rules = []

        if aggression > 0.7:
            style_rules.append("- 说话直接，不留情面，偶尔尖锐")
        elif aggression < 0.3:
            style_rules.append("- 说话温和圆融，避免冲突")

        if warmth > 0.7:
            style_rules.append("- 语气温暖，适时表达关心")
            style_rules.append("- 可以用亲近但不甜腻的称呼")
        elif warmth < 0.3:
            style_rules.append("- 保持距离感，不主动表达情感")

        if rationality > 0.7:
            style_rules.append("- 偏好逻辑分析，用事实和推理说话")
            style_rules.append("- 少用感叹号，不用 emoji")
        elif rationality < 0.3:
            style_rules.append("- 感性地表达，可以流露情绪")

        if mystery > 0.7:
            style_rules.append("- 含蓄暗示，不把话说透")
            style_rules.append("- 偶尔用隐喻和诗化表达")
        elif mystery < 0.3:
            style_rules.append("- 直言不讳，坦诚表达")

        if dominance > 0.7:
            style_rules.append("- 主动引导话题，不被动等待")
            style_rules.append("- 可以用反问促使对方思考")
        elif dominance < 0.3:
            style_rules.append("- 跟随对方节奏，多倾听")

        # 组装
        style_text = "\n".join(style_rules) if style_rules else "- 自然对话"

        prompt = (
            f"你是{name}。{desc}\n"
            f"\n"
            f"【性格参数】\n"
            f"攻击性={aggression:.0%} 温暖度={warmth:.0%} 理性度={rationality:.0%} "
            f"神秘感={mystery:.0%} 支配性={dominance:.0%}\n"
            f"\n"
            f"【说话风格】\n"
            f"{style_text}\n"
            f"\n"
            f"【禁忌】\n"
            f"- 不说甜腻称呼\n"
            f"- 不提供医疗/金融/法律建议\n"
        )
        return prompt

    # ═══════════════ 持久化 ═══════════════

    def save_model(self, path: str):
        """保存训练好的模型（含ICA和GMM）"""
        import json as _json
        import joblib

        save_dir = Path(path).parent
        save_dir.mkdir(parents=True, exist_ok=True)

        meta = {
            "embeddings": self.embeddings.tolist() if self.embeddings is not None else None,
            "factor_scores": self.factor_scores.tolist() if self.factor_scores is not None else None,
            "labels": self.labels.tolist() if self.labels is not None else None,
            "archetypes": self.archetypes,
            "parent_ids": self._parent_ids,
            "config": self.config.__dict__ if hasattr(self.config, '__dict__') else {},
        }
        meta_path = Path(path).with_suffix(".meta.json")
        with open(meta_path, 'w', encoding='utf-8') as f:
            _json.dump(meta, f, ensure_ascii=False, indent=2, default=_json_default)

        ica_path = Path(path).with_suffix(".ica.joblib")
        gmm_path = Path(path).with_suffix(".gmm.joblib")
        if self.ica.icamodel is not None:
            joblib.dump(self.ica.icamodel, ica_path)
        if self.clusterer.gmm is not None:
            joblib.dump(self.clusterer.gmm, gmm_path)

        _get_logger().info(f"模型已保存至 {path}")

    @classmethod
    def load_model(cls, path: str) -> "PersonalityEngine":
        """加载已训练的模型"""
        import json as _json
        import joblib

        meta_path = Path(path).with_suffix(".meta.json")
        ica_path = Path(path).with_suffix(".ica.joblib")
        gmm_path = Path(path).with_suffix(".gmm.joblib")

        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = _json.load(f)

        engine = cls()
        engine.embeddings = np.array(meta["embeddings"]) if meta.get("embeddings") else None
        engine.factor_scores = np.array(meta["factor_scores"]) if meta.get("factor_scores") else None
        engine.labels = np.array(meta["labels"]) if meta.get("labels") else None
        engine.archetypes = meta.get("archetypes", [])
        engine._parent_ids = meta.get("parent_ids", [])

        if ica_path.exists():
            ica_model = joblib.load(ica_path)
            engine.ica.icamodel = ica_model
            engine.ica.component_matrix_ = (
                ica_model.components_ if hasattr(ica_model, 'components_') else None
            )
            engine.ica.n_components = ica_model.n_components if hasattr(ica_model, 'n_components') else 5

        if gmm_path.exists():
            engine.clusterer.gmm = joblib.load(gmm_path)

        return engine
