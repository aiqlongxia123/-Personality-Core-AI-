"""人格维度定义与默认配置"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Dimension:
    """一个人格维度"""
    id: str
    name_zh: str
    name_en: str
    pole_a_label: str  # 低分端
    pole_b_label: str  # 高分端
    default_weight: float = 1.0


DIMENSIONS = [
    Dimension("openness", "开放性", "Openness", "保守传统", "创新冒险"),
    Dimension("conscientiousness", "尽责性", "Conscientiousness", "随性散漫", "严谨自律"),
    Dimension("extraversion", "外向性", "Extraversion", "内向独处", "社交活跃"),
    Dimension("agreeableness", "宜人性", "Agreeableness", "竞争对抗", "合作共情"),
    Dimension("neuroticism", "神经质", "Neuroticism", "情绪稳定", "敏感多虑"),
    Dimension("dominance", "支配性", "Dominance", "服从配合", "主导控制"),
    Dimension("aggression", "攻击性", "Aggression", "温和包容", "尖锐直接"),
    Dimension("mystery", "神秘感", "Mystery", "坦诚直白", "隐晦暧昧"),
    Dimension("warmth", "温暖度", "Warmth", "冷漠疏离", "热情亲密"),
    Dimension("rationality", "理性度", "Rationality", "感性冲动", "冷静分析"),
]

# 维度ID → 索引映射
DIMENSION_INDEX = {d.id: i for i, d in enumerate(DIMENSIONS)}
N_DIMENSIONS = len(DIMENSIONS)


@dataclass
class PersonalityConfig:
    """人格系统全局配置"""
    n_factors: int = 10
    n_clusters: int = 6
    embedder_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    morph_default_angle: float = 30.0
    mood_smoothing_weight: float = 0.6
    mood_random_probability: float = 0.3
    mood_random_range: float = 0.1
    relationship_thresholds: tuple = (0.3, 0.6)


DEFAULT_CONFIG = PersonalityConfig()
