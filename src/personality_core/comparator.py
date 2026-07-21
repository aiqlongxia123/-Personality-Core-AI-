"""人格对比模块 — 两个人格在因子维度上的差异分析"""
import numpy as np
from typing import Optional


class PersonalityComparator:
    """对比两个人格在各个因子维度上的差异"""

    def __init__(self):
        pass

    def compare(
        self,
        person_a: np.ndarray,
        person_b: np.ndarray,
        name_a: str = "A",
        name_b: str = "B",
        factor_labels: Optional[list] = None,
    ) -> dict:
        """
        对比两个人格。

        person_a/b: 在因子空间中的得分向量
        factor_labels: 可选，因子标签列表（Dimension对象或dict）
        """
        a = np.asarray(person_a, dtype=float)
        b = np.asarray(person_b, dtype=float)

        if len(a) != len(b):
            raise ValueError("两个人格的维度数必须一致")

        n_dims = len(a)
        diffs = b - a

        results = []
        for i in range(n_dims):
            if factor_labels and i < len(factor_labels):
                label = factor_labels[i]
                if hasattr(label, 'name_zh'):
                    dim_name = label.name_zh
                    dim_id = label.id
                    pole_a = label.pole_a_label
                    pole_b = label.pole_b_label
                elif isinstance(label, dict):
                    dim_name = label.get("name_zh", f"因子_{i}")
                    dim_id = label.get("factor_index", i)
                    pole_a = label.get("pole_a", "")
                    pole_b = label.get("pole_b", "")
                else:
                    dim_name = f"因子_{i}"
                    dim_id = f"f{i}"
                    pole_a = ""
                    pole_b = ""
            else:
                dim_name = f"因子_{i}"
                dim_id = f"f{i}"
                pole_a = ""
                pole_b = ""

            results.append({
                "dimension_id": dim_id,
                "dimension_name": dim_name,
                "score_a": round(float(a[i]), 4),
                "score_b": round(float(b[i]), 4),
                "delta": round(float(diffs[i]), 4),
                "pole_a": pole_a,
                "pole_b": pole_b,
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
