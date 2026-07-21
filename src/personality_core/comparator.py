"""人格对比模块 — 两个人格在多维度上的差异分析"""
import numpy as np
from .config import DIMENSIONS


class PersonalityComparator:
    """对比两个人格在各个维度上的差异"""

    def __init__(self):
        self.dimensions = DIMENSIONS

    def compare(
        self,
        person_a: np.ndarray,
        person_b: np.ndarray,
        name_a: str = "A",
        name_b: str = "B",
    ) -> dict:
        """
        对比两个人格。

        person_a/b: 在统一维度空间中的得分向量（长度=N_DIMENSIONS）
        返回每个人的各维度得分 + 差值 + 百分位标签
        """
        a = np.asarray(person_a, dtype=float)
        b = np.asarray(person_b, dtype=float)

        if len(a) != len(b):
            raise ValueError("两个人格的维度数必须一致")

        n_dims = len(a)
        diffs = b - a  # 从A到B的变化

        results = []
        for i in range(n_dims):
            dim = self.dimensions[i] if i < len(self.dimensions) else None
            results.append({
                "dimension_id": dim.id if dim else f"d{i}",
                "dimension_name": dim.name_zh if dim else f"维度{i}",
                "score_a": round(float(a[i]), 4),
                "score_b": round(float(b[i]), 4),
                "delta": round(float(diffs[i]), 4),
                "pole_a": dim.pole_a_label if dim else "",
                "pole_b": dim.pole_b_label if dim else "",
            })

        dominant_shift = max(results, key=lambda x: abs(x["delta"]))
        return {
            "person_a": name_a,
            "person_b": name_b,
            "dimensions": results,
            "biggest_shift": {
                "dimension": dominant_shift["dimension_name"],
                "direction": (
                    dominant_shift["pole_b"] if dominant_shift["delta"] > 0
                    else dominant_shift["pole_a"]
                ),
                "magnitude": round(abs(dominant_shift["delta"]), 4),
            },
        }
