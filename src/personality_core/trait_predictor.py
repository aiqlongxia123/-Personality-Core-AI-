"""Trait 预测器 — 从文本描述预测人格特质（监督回归）"""
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.multioutput import MultiOutputRegressor
from pathlib import Path


TRAIT_NAMES = ["aggression", "warmth", "mystery", "rationality", "dominance"]


class TraitPredictor:
    """从文本 embedding 预测 5 维人格特质。

    与 ICA/GMM 不同，这个模型使用人工标注的 trait 标签做监督回归。
    embedding → Ridge → {aggression, warmth, mystery, rationality, dominance}
    每个值 ∈ [0, 1]。
    """

    def __init__(self):
        self.model: MultiOutputRegressor | None = None
        self.embedder = None  # 需外部注入 TextEmbedder

    def fit(self, embedder, texts: list[str], traits_list: list[dict]):
        """训练回归模型。

        texts: 人格描述文本列表
        traits_list: 对应的 trait 字典列表，每个含 aggression/warmth/...
        """
        self.embedder = embedder
        X = embedder.encode(texts)  # (n, 384)
        y = np.array([
            [float(t.get(name, 0.5)) for name in TRAIT_NAMES]
            for t in traits_list
        ])  # (n, 5)

        self.model = MultiOutputRegressor(Ridge(alpha=1.0, random_state=42))
        self.model.fit(X, y)
        return self

    def predict(self, text: str) -> dict:
        """从单条文本预测 5 维特质"""
        if self.model is None or self.embedder is None:
            raise RuntimeError("TraitPredictor 未训练")
        vec = self.embedder.encode_single(text).reshape(1, -1)
        raw = self.model.predict(vec)[0]
        # 裁剪到 [0, 1]
        clipped = np.clip(raw, 0.0, 1.0)
        return {name: round(float(clipped[i]), 4) for i, name in enumerate(TRAIT_NAMES)}

    def predict_batch(self, texts: list[str]) -> list[dict]:
        """批量预测"""
        if self.model is None or self.embedder is None:
            raise RuntimeError("TraitPredictor 未训练")
        X = self.embedder.encode(texts)
        raw = self.model.predict(X)
        clipped = np.clip(raw, 0.0, 1.0)
        return [
            {name: round(float(clipped[i, j]), 4) for j, name in enumerate(TRAIT_NAMES)}
            for i in range(len(texts))
        ]

    def save(self, path: str):
        import joblib
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)

    @classmethod
    def load(cls, path: str, embedder) -> "TraitPredictor":
        import joblib
        tp = cls()
        tp.model = joblib.load(path)
        tp.embedder = embedder
        return tp


def train_from_archetypes(engine: "PersonalityEngine") -> TraitPredictor:
    """从引擎的内置人格档案训练 TraitPredictor。

    使用 BUILTIN_PERSONAS 中 11 个人格的 description + traits 作为训练数据。
    """
    from personality_core.engine import BUILTIN_PERSONAS

    texts = []
    traits_list = []
    for pid, p in BUILTIN_PERSONAS.items():
        if p.description and p.traits:
            texts.append(p.description)
            traits_list.append(p.traits)

    tp = TraitPredictor()
    tp.fit(engine.embedder, texts, traits_list)
    return tp
