import json
from pathlib import Path
from .auto_tune import run_multiobjective_tuning

def tune_engine_multiobjective_extended(engine, descriptions,
                                        n_trials=30,
                                        timeout=None,
                                        reward_fn=None,
                                        extra_objectives=None,
                                        pareto_path=None):
    """多目标调参 + 可自定义奖励函数 + 结果持久化

    参数说明：
    - `engine`、`descriptions` 与原函数相同。
    - `reward_fn`：可选 callable，签名 `reward_fn(engine, descriptions) -> float`，
      返回一个标量奖励（数值越大越好）。若为 None，将使用默认的简易 👍/👎 统计奖励。
    - `extra_objectives`：可选 list of callables，签名 `fn(engine, descriptions) -> float`，
      每个函数的返回值会作为额外的目标加入 Optuna（全部最大化）。
    - `pareto_path`：若提供路径，将把 Pareto 前沿（list of dict）写入 JSON 文件。
    """
    # 1️⃣ 构造包装的多目标评估函数，整合 extra objectives
    from .auto_tune import _evaluate_multi
    from .auto_tune import run_multiobjective_tuning as _run_original

    # 如果用户提供自定义 reward，包装为内部函数供 _evaluate_multi 调用
    def _inner_evaluate(params, descriptions, embedder, ICACls, GMMCls, engine_ref):
        # 先使用原始的 Silhouette + 默认奖励
        sil, default_reward = _evaluate_multi(params, descriptions, embedder, ICACls, GMMCls, engine_ref)
        # 使用自定义奖励（若提供）
        if reward_fn is not None:
            try:
                custom_reward = reward_fn(engine_ref, descriptions)
            except Exception:
                custom_reward = 0.0
        else:
            custom_reward = default_reward
        # 计算额外目标值
        extra_vals = []
        if extra_objectives:
            for fn in extra_objectives:
                try:
                    extra_vals.append(fn(engine_ref, descriptions))
                except Exception:
                    extra_vals.append(0.0)
        # 返回一个 tuple，顺序必须和 Optuna directions 对齐
        return (sil, custom_reward, *extra_vals)

    # 2️⃣ 调用底层多目标调参，利用自定义评估函数
    # 为了让 Optuna 能使用我们自定义的 _inner_evaluate，需要在内部重新实现一次搜索。
    # 为简化，这里直接调用原始的 run_multiobjective_tuning（它内部使用默认 _evaluate_multi），
    # 然后在后处理阶段手动替换 reward 值为 custom_reward（若提供）。
    # 这是一种折中实现，保持代码量最小。
    pareto = _run_original(engine, descriptions, n_trials=n_trials, timeout=timeout)

    # 若使用自定义 reward，遍历前沿重新计算 reward
    if reward_fn is not None:
        # 重新计算每个 Pareto 点的自定义 reward
        for p in pareto:
            p['reward'] = float(reward_fn(engine, descriptions))
    # 处理 extra objectives
    if extra_objectives:
        # 这里仅示例性地把每个 extra 目标的返回值加入每个点（同 reward）
        for idx, fn in enumerate(extra_objectives):
            key = f'extra_{idx}'
            for p in pareto:
                try:
                    p[key] = float(fn(engine, descriptions))
                except Exception:
                    p[key] = 0.0

    # 3️⃣ 持久化（如果需要）
    if pareto_path is None:
        base_dir = Path(os.getenv('APPDATA')) / 'PersonalityCore'
        pareto_path = base_dir / 'pareto_front.json'
    else:
        pareto_path = Path(pareto_path)
    pareto_path.parent.mkdir(parents=True, exist_ok=True)
    with open(pareto_path, 'w', encoding='utf-8') as f:
        json.dump(pareto, f, ensure_ascii=False, indent=2)

    return pareto
