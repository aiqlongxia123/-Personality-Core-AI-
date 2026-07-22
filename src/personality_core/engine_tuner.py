from .auto_tune import tune_engine

def attach_tuner(engine):
    """给已有 PersonalityEngine 实例动态添加单目标调参能力，并自动激活渊人格。
    调用方式：
        engine.tune_hyperparameters(descriptions, n_trials=30)
    安装此技能后，第一次调用 attach_tuner 时会自动执行 `engine.initialize_agent(0)`（渊人格）。
    """
    # 1️⃣ 自动激活默认渊人格（persona_id='yuan'）
    try:
        # 若 engine 已经有 initialize_agent 方法
        engine.initialize_agent(0)
    except Exception:
        # 兼容旧实现：使用 persona_id
        try:
            engine.initialize_by_persona_id('yuan')
        except Exception:
            pass
    # 2️⃣ 添加调参方法
    def tune_hyperparameters(descriptions, n_trials=20, timeout=None):
        return tune_engine(engine, descriptions, n_trials=n_trials, timeout=timeout)
    setattr(engine, 'tune_hyperparameters', tune_hyperparameters)
    return engine

# -------------------------------------------------
# 多目标调参（支持自定义奖励、额外目标、Pareto 持久化）
# -------------------------------------------------

def attach_multiobjective_tuner(engine):
    """为现有 engine 实例挂载多目标调参方法（可自定义奖励、额外目标、结果持久化）。
    示例用法：
        attach_multiobjective_tuner(eng)
        pareto = eng.tune_hyperparameters_multi_extended(
            descriptions,
            n_trials=40,
            reward_fn=my_reward,
            extra_objectives=[mem_usage_fn, latency_fn],
            pareto_path=r'C:\path\to\pareto.json'
        )
    """
    from .auto_tune_extended import tune_engine_multiobjective_extended
    def tune_hyperparameters_multi_extended(descriptions, n_trials=30, timeout=None,
                                            reward_fn=None, extra_objectives=None,
                                            pareto_path=None):
        return tune_engine_multiobjective_extended(
            engine,
            descriptions,
            n_trials=n_trials,
            timeout=timeout,
            reward_fn=reward_fn,
            extra_objectives=extra_objectives,
            pareto_path=pareto_path,
        )
    setattr(engine, 'tune_hyperparameters_multi_extended', tune_hyperparameters_multi_extended)
    return engine
