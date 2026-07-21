"""人格评分模块 — 语义相似度与场景匹配"""
import numpy as np


class PersonalityScorer:
    """计算两个向量之间的语义相似度（非心理学适配度）"""

    def __init__(self):
        pass

    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """余弦相似度"""
        a_norm = a / (np.linalg.norm(a) + 1e-10)
        b_norm = b / (np.linalg.norm(b) + 1e-10)
        return float(np.dot(a_norm, b_norm))

    @staticmethod
    def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
        """欧氏距离"""
        return float(np.linalg.norm(a - b))

    def score_pairing(self, person_a: np.ndarray, person_b: np.ndarray) -> dict:
        """计算两个向量的语义相似度。

        对于单位向量，cosine_similarity ∈ [-1, 1]。
        映射到 [0, 1] 区间：similarity = (cos_sim + 1) / 2。
        """
        cos_sim = self.cosine_similarity(person_a, person_b)
        dist = self.euclidean_distance(person_a, person_b)

        # 语义接近度：映射到 0~1
        similarity = round((cos_sim + 1.0) / 2.0, 4)

        return {
            "cosine_similarity": round(cos_sim, 4),
            "euclidean_distance": round(dist, 4),
            "similarity": similarity,
            "label": self._label(similarity),
        }

    def score_scenario_fit(
        self,
        personality: np.ndarray,
        scenario_vector: np.ndarray,
    ) -> dict:
        """评估某个人格向量对某个场景向量的接近度"""
        cos_sim = self.cosine_similarity(personality, scenario_vector)
        fit_score = round((cos_sim + 1.0) / 2.0, 4)
        return {
            "fit_score": fit_score,
            "label": self._label(fit_score),
        }

    @staticmethod
    def _label(score: float) -> str:
        """语义接近度标签（非心理适配度）"""
        if score >= 0.9:
            return "极高相似"
        elif score >= 0.75:
            return "高相似"
        elif score >= 0.5:
            return "中等相似"
        elif score >= 0.3:
            return "低相似"
        else:
            return "极低相似/语义相反"
