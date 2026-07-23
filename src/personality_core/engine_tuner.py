# engine 调参依赖 optuna, 延迟导入以免阻塞 route_by_tone / attach_tuner
_tune_engine = None

def _get_tune_engine():
    global _tune_engine
    if _tune_engine is None:
        from .auto_tune import tune_engine

        _tune_engine = tune_engine
    return _tune_engine

# 软化情绪词映射: 委婉语言 → 推荐人格 id
# 在 chat() 前用 route_by_tone(user_input) 探测, 由调用方决定是否切换.
_TONE_MAP: dict[str, str] = {
    # 暴躁娘们 — 触发词: 委婉表达愤怒/绝望
    "痛苦": "baozao_niangmen",
    "算了吧": "baozao_niangmen",
    "没意思": "baozao_niangmen",
    "累了": "baozao_niangmen",
    "算了": "baozao_niangmen",
    "烂透了": "baozao_niangmen",
    # 清晏 — 触发词: 寻求温柔陪伴
    "害怕": "qingyan",
    "孤独": "qingyan",
    "陪我": "qingyan",
    "想哭": "qingyan",
    # 尼采的魔鬼 — 触发词: 寻求决断/锻造
    "软弱": "nietzsche_devil",
    "振作": "nietzsche_devil",
    "站起来": "nietzsche_devil",
}


def attach_tuner(engine, *, default_persona_id: str = "yuan", activate_now: bool = True):
    """给已有 PersonalityEngine 实例动态添加单目标调参能力, 并自动激活默认人格.

    与旧版不同:
      - 优先按 persona_id 激活 (initialize_by_persona_id), 不依赖 train 后的聚类顺序.
      - 若 train 未执行, 退回 initialize_agent(0).
      - 不强制激活: 设 activate_now=False 只挂载调参方法.

    调用方式::

        from personality_core.engine import PersonalityEngine
        from personality_core.engine_tuner import attach_tuner

        engine = PersonalityEngine()
        engine.train(descriptions)
        attach_tuner(engine)                      # 自动激活渊
        attach_tuner(engine, activate_now=False)  # 只挂载, 不激活

        engine.tune_hyperparameters(descriptions, n_trials=30)
    """
    # 1️⃣ 激活默认人格
    if activate_now:
        activated = False
        try:
            engine.initialize_by_persona_id(default_persona_id)
            activated = True
        except (RuntimeError, ValueError, AttributeError):
            pass
        if not activated:
            try:
                engine.initialize_agent(0)
            except Exception:
                pass

    # 2️⃣ 挂载单目标调参方法
    def tune_hyperparameters(descriptions, n_trials=20, timeout=None):
        return _get_tune_engine()(engine, descriptions, n_trials=n_trials, timeout=timeout)

    setattr(engine, "tune_hyperparameters", tune_hyperparameters)

    # 3️⃣ 暴露情绪词路由方法 (轻量耦合: 不自动切换, 仅给调用方建议)
    setattr(engine, "route_by_tone", lambda text: route_by_tone(text))

    return engine


def route_by_tone(text: str) -> str | None:
    """根据输入文本的关键词, 推荐一个人格 id. 不做切换, 仅做建议.

    命中_TONE_MAP 中的任意委婉词, 返回对应人格 id;
    否则返回 None (沿用当前人格).
    """
    if not text:
        return None
    for keyword, persona_id in _TONE_MAP.items():
        if keyword in text:
            return persona_id
    return None


# -------------------------------------------------
# 多目标调参 (保持向后兼容)
# -------------------------------------------------
def attach_multiobjective_tuner(engine):
    """为现有 engine 实例挂载多目标调参方法 (可自定义奖励、额外目标、结果持久化)."""
    from .auto_tune_extended import tune_engine_multiobjective_extended

    def tune_hyperparameters_multi_extended(
        descriptions, n_trials=30, timeout=None,
        reward_fn=None, extra_objectives=None, pareto_path=None,
    ):
        return tune_engine_multiobjective_extended(
            engine, descriptions,
            n_trials=n_trials, timeout=timeout,
            reward_fn=reward_fn, extra_objectives=extra_objectives,
            pareto_path=pareto_path,
        )

    setattr(engine, "tune_hyperparameters_multi_extended", tune_hyperparameters_multi_extended)
    return engine
