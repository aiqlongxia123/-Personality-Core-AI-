"""人格向量旋转（Morph）— 沿方向轴正交旋转种子人格"""
import numpy as np


def morph_vector(
    seed: np.ndarray,
    direction: np.ndarray,
    angle_deg: float = 30.0,
) -> np.ndarray:
    """
    在单位球面上将 seed 向 direction 的**正交分量**旋转 angle_deg 度。

    正确实现：
    1. 归一化 seed
    2. 将 direction 分解为平行分量 + 正交分量
    3. 使用正交分量作为旋转轴
    4. seed * cos(θ) + direction_orthogonal * sin(θ)

    角度参考：
      0°  = seed不变 (cos=1.00)
     15°  = 微妙偏移 (cos=0.97)
     30°  = 轻度变形 (cos=0.87)
     45°  = 均衡混合 (cos=0.71)
     60°  = 强烈变形 (cos=0.50)
     90°  = 完全正交 (cos=0)
    """
    angle_rad = np.radians(angle_deg)
    cos_a = np.cos(angle_rad)
    sin_a = np.sin(angle_rad)

    # 归一化 seed
    seed_norm = seed / (np.linalg.norm(seed) + 1e-10)
    # 归一化 direction
    dir_norm = direction / (np.linalg.norm(direction) + 1e-10)

    # 正交分解：direction = 平行分量(沿seed) + 正交分量(⊥seed)
    parallel_component = np.dot(dir_norm, seed_norm) * seed_norm
    orthogonal_component = dir_norm - parallel_component

    orth_norm = np.linalg.norm(orthogonal_component)
    if orth_norm < 1e-10:
        # direction 与 seed 完全共线 → 无法旋转，返回 seed
        return seed_norm.copy()

    direction_orth = orthogonal_component / orth_norm

    # 球面旋转
    result = seed_norm * cos_a + direction_orth * sin_a
    result = result / (np.linalg.norm(result) + 1e-10)
    return result


def morph_from_poles(
    seed: np.ndarray,
    pole_a: np.ndarray,
    pole_b: np.ndarray,
    ratio: float = 0.5,
) -> np.ndarray:
    """
    在两个极点之间按比例混合后旋转种子。

    ratio=0 → pole_a 方向, ratio=1 → pole_b 方向, ratio=0.5 → 中间
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

    new_scores = np.clip(new_scores, -3.0, 3.0)
    return new_scores
