"""人格向量旋转（Morph）— 沿方向轴正交旋转种子人格"""
import numpy as np


MAX_MORPH_NORM = 1.5  # 限制旋转向量最大模长，防止数值溢出
MAX_ANGLE_DEG = 90.0


def _clamp_vector(vector: np.ndarray, max_norm: float = MAX_MORPH_NORM) -> np.ndarray:
    """将向量模长钳制到安全范围"""
    norm = np.linalg.norm(vector)
    if norm > max_norm:
        print(f"[Morph警告] 检测到超限旋转向量 (norm={norm:.4f})，已自动截断至 {max_norm}")
        vector = vector / norm * max_norm
    return vector


def morph_vector(
    seed: np.ndarray,
    direction: np.ndarray,
    angle_deg: float = 30.0,
) -> np.ndarray:
    """
    在单位球面上将 seed 向 direction 的**正交分量**旋转 angle_deg 度。

    安全钳制：
    - angle_deg 限制在 [0, MAX_ANGLE_DEG]
    - direction 向量模长钳制到 MAX_MORPH_NORM
    - 结果始终归一化，防止数值膨胀
    """
    # 钳制角度
    angle_deg = max(0.0, min(angle_deg, MAX_ANGLE_DEG))

    # 钳制旋转向量模长
    direction = _clamp_vector(direction)

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
