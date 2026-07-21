"""人格评分模块 — 适配度打分与场景匹配"""
import numpy as np


class PersonalityScorer:
    """计算两个人格/场景之间的适配度"""

    def __init__(self):
        pass

    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """余弦相似度"""
        a = a / (np.linalg.norm(a) + 1e-10)
        b = b / (np.linalg.norm(b) + 1e-10)
        return float(np.dot(a, b))

    @staticmethod
    def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
        """欧氏距离"""
        return float(np.linalg.norm(a - b))

    def score_pairing(self, person_a: np.ndarray, person_b: np.ndarray) -> dict:
        """计算两个人格的配对分数"""
        cos_sim = self.cosine_similarity(person_a, person_b)
        dist = self.euclidean_distance(person_a, person_b)

        # 归一化距离到0~1（假设最大距离约2）
        norm_dist = min(dist / 2.0, 1.0)
        compatibility = (cos_sim + (1 - norm_dist)) / 2.0

        return {
            "cosine_similarity": round(cos_sim, 4),
            "euclidean_distance": round(dist, 4),
            "compatibility": round(compatibility, 4),
            "label": self._label(compatibility),
        }

    def score_scenario_fit(
        self,
        personality: np.ndarray,
        scenario_vector: np.ndarray,
    ) -> dict:
        """评估某个人格对某个场景的适配度"""
        cos_sim = self.cosine_similarity(personality, scenario_vector)
        return {
            "fit_score": round((cos_sim + 1) / 2, 4),  # 映射到0~1
            "label": self._label((cos_sim + 1) / 2),
        }

    @staticmethod
    def _label(score: float) -> str:
        if score >= 0.8:
            return "极高适配"
        elif score >= 0.6:
            return "高适配"
        elif score >= 0.4:
            return "中等适配"
        elif score >= 0.2:
            return "低适配"
        else:
            return "极低适配"
