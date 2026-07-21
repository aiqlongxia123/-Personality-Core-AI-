"""人格向量旋转（Morph）— 沿方向轴旋转种子人格"""
import numpy as np


def morph_vector(
    seed: np.ndarray,
    direction: np.ndarray,
    angle_deg: float = 30.0,
) -> np.ndarray:
    """
    在单位球面上将seed向量向direction方向旋转angle_deg度。

    角度参考：
      0°  = seed不变 (cos=1.00)
     15°  = 微妙偏移 (cos=0.97)
     30°  = 轻度变形 (cos=0.87)
     45°  = 均衡混合 (cos=0.71)
     60°  = 强烈变形 (cos=0.50)
     90°  = 完全正交，原始身份被丢弃 (cos=0)
    """
    angle_rad = np.radians(angle_deg)
    cos_a = np.cos(angle_rad)
    sin_a = np.sin(angle_rad)

    # 确保方向向量归一化
    dir_norm = direction / (np.linalg.norm(direction) + 1e-10)

    # 球面线性插值（简化版slerp）
    result = seed * cos_a + dir_norm * sin_a
    # 重新归一化到单位球面
    result = result / (np.linalg.norm(result) + 1e-10)
    return result


def morph_from_poles(
    seed: np.ndarray,
    pole_a: np.ndarray,
    pole_b: np.ndarray,
    ratio: float = 0.5,
) -> np.ndarray:
    """
    在两个极点之间按比例混合。

    ratio=0 → pole_a方向, ratio=1 → pole_b方向, ratio=0.5 → 中间
    """
    blended = pole_a * (1 - ratio) + pole_b * ratio
    blended = blended / (np.linalg.norm(blended) + 1e-10)
    return morph_vector(seed, blended, angle_deg=30.0)


def morph_factor_score(
    factor_scores: np.ndarray,
    factor_index: int,
    direction: str = "toward_b",
    magnitude: float = 0.3,
) -> np.ndarray:
    """
    直接在因子得分上操作，改变某个因子的得分。

    factor_index: 要修改的因子索引
    direction: "toward_b"（增大）或 "toward_a"（减小）
    magnitude: 变化幅度 0~1
    """
    new_scores = factor_scores.copy()
    if direction == "toward_b":
        new_scores[:, factor_index] += magnitude
    elif direction == "toward_a":
        new_scores[:, factor_index] -= magnitude
    else:
        raise ValueError(f"未知方向: {direction}")

    # 裁剪到合理范围
    new_scores = np.clip(new_scores, -3.0, 3.0)
    return new_scores
