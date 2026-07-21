"""ICA因子提取模块 — 从人格向量中解混出独立维度"""
import numpy as np
from sklearn.decomposition import FastICA
from .config import DIMENSIONS, Dimension


class ICAExtractor:
    """独立成分分析：把混合的人格向量分解为独立的因子"""

    def __init__(self, n_components: int = 10):
        self.n_components = n_components
        self.icamodel = None
        self.factors: list[Dimension] = []
        self.component_matrix_ = None

    def fit(self, embeddings: np.ndarray) -> "ICAExtractor":
        """训练ICA模型，从嵌入矩阵中提取独立因子"""
        self.icamodel = FastICA(
            n_components=self.n_components,
            random_state=42,
            algorithm="parallel",
        )
        self.component_matrix_ = self.icamodel.fit_transform(embeddings)
        self._assign_labels()
        return self

    def transform(self, embeddings: np.ndarray) -> np.ndarray:
        """对新数据做因子得分变换"""
        if self.icamodel is None:
            raise RuntimeError("ICAExtractor未训练，请先调用fit()")
        return self.icamodel.transform(embeddings)

    def inverse_transform(self, factors: np.ndarray) -> np.ndarray:
        """从因子得分还原为嵌入空间"""
        if self.icamodel is None:
            raise RuntimeError("ICAExtractor未训练，请先调用fit()")
        return self.icamodel.inverse_transform(factors)

    def _assign_labels(self):
        """为每个因子分配标签（基于训练数据的pole方向）"""
        # 因子标签来自预定义维度；实际项目中可通过代表性样本自动标注
        self.factors = DIMENSIONS[: self.n_components]

    def get_factor_labels(self) -> list[dict]:
        """返回所有因子的可读标签"""
        result = []
        for i, dim in enumerate(self.factors):
            result.append({
                "factor_index": i,
                "name_zh": dim.name_zh,
                "name_en": dim.name_en,
                "pole_a": dim.pole_a_label,
                "pole_b": dim.pole_b_label,
            })
        return result
