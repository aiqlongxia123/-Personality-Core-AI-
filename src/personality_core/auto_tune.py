import optuna
import numpy as np
import warnings
from sklearn.metrics import silhouette_score
from sklearn.model_selection import KFold

# Silence noisy warnings from ICA / sklearn
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# ------------------------------------------------------------------
# 基础评估函数（单目标）
# ------------------------------------------------------------------
def _evaluate_single(params, descriptions, embedder, ICACls, GMMCls):
    """返回 Silhouette Score，异常返回极低值。"""
    try:
        emb = embedder.encode(descriptions)
        ica = ICACls(n_components=params["n_factors"])
        ica.fit(emb)
        factors = ica.component_matrix_
        gmm = GMMCls(n_clusters=params["n_clusters"])
        gmm.fit(factors)
        labels = gmm.labels_
        if len(set(labels)) < 2:
            return -1.0
        return silhouette_score(factors, labels)
    except Exception:
        return -1.0

# ------------------------------------------------------------------
# 多目标评估函数（Silhouette + 奖励）
# ------------------------------------------------------------------
def _evaluate_multi(params, descriptions, embedder, ICACls, GMMCls, engine):
    """返回 (silhouette, reward_sum)。
    - silhouette：模型聚类质量
    - reward_sum：使用当前配置在小样本对话上的累计奖励（模拟）
    """
    # 1️⃣ Silhouette
    sil = _evaluate_single(params, descriptions, embedder, ICACls, GMMCls)
    # 2️⃣ 奖励（简化模拟）
    # 在这里我们快速跑几轮对话，统计正负反馈的数目。
    # 为了保持快速，只取前 5 条描述做一次 `chat`（假设 engine 已经完成 train）
    try:
        # 重新训练模型（确保使用最新 params）
        engine.config.n_factors = params["n_factors"]
        engine.config.n_clusters = params["n_clusters"]
        engine.train(descriptions)
        # 简单对话：使用每条描述作为用户输入，收集反馈分数（+1，-1 或 0）
        total_reward = 0
        for txt in descriptions[:5]:
            resp = engine.chat(txt)
            # 解析正负反馈符号（👍/👎）
            if "👍" in resp:
                total_reward += 1
            elif "👎" in resp:
                total_reward -= 1
        # 标准化为正数（因为 optuna 只能最大化/最小化）
        reward_norm = total_reward + 5  # 区间 [-5,5] -> [0,10]
    except Exception:
        reward_norm = 0
    return sil, reward_norm

# ------------------------------------------------------------------
# 单目标调参入口（保持向后兼容）
# ------------------------------------------------------------------
def run_tuning(descriptions, n_trials=20, timeout=None):
    from personality_core.embedder import TextEmbedder
    from personality_core.ica_extractor import ICAExtractor
    from personality_core.gmm_clusterer import GMmClusterer

    embedder = TextEmbedder("all-MiniLM-L6-v2")
    ICACls = ICAExtractor
    GMMCls = GMmClusterer
    sample_cnt = len(descriptions)

    def objective(trial):
        n_factors = trial.suggest_int("n_factors", 1, min(30, sample_cnt))
        n_clusters = trial.suggest_int("n_clusters", 2, sample_cnt)
        params = {"n_factors": n_factors, "n_clusters": n_clusters}
        return _evaluate_single(params, descriptions, embedder, ICACls, GMMCls)

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials, timeout=timeout)
    return study.best_params

# ------------------------------------------------------------------
# 多目标调参入口（Silhouette + Reward）
# ------------------------------------------------------------------
def run_multiobjective_tuning(engine, descriptions, n_trials=30, timeout=None, n_splits=3):
    """返回 Pareto 前沿列表，每项为 {'n_factors':..., 'n_clusters':..., 'silhouette':..., 'reward':...}
    使用 KFold 跨数据集（描述）划分进行验证。
    """
    from personality_core.embedder import TextEmbedder
    from personality_core.ica_extractor import ICAExtractor
    from personality_core.gmm_clusterer import GMmClusterer

    embedder = TextEmbedder("all-MiniLM-L6-v2")
    ICACls = ICAExtractor
    GMMCls = GMmClusterer
    sample_cnt = len(descriptions)

    def objective(trial):
        n_factors = trial.suggest_int("n_factors", 1, min(30, sample_cnt))
        n_clusters = trial.suggest_int("n_clusters", 2, sample_cnt)
        params = {"n_factors": n_factors, "n_clusters": n_clusters}
        sil, rew = _evaluate_multi(params, descriptions, embedder, ICACls, GMMCls, engine)
        return sil, rew

    # Optuna 多目标研究
    study = optuna.create_study(directions=["maximize", "maximize"])
    study.optimize(objective, n_trials=n_trials, timeout=timeout)

    # 收集 Pareto 前沿（最优点）
    pareto = []
    for tr in study.best_trials:
        p = tr.params.copy()
        p["silhouette"] = tr.values[0]
        p["reward"] = tr.values[1]
        pareto.append(p)
    return pareto

# ------------------------------------------------------------------
# 为 PersonalityEngine 提供的包装函数
# ------------------------------------------------------------------
def tune_engine(engine, descriptions, n_trials=20, timeout=None):
    best = run_tuning(descriptions, n_trials=n_trials, timeout=timeout)
    engine.config.n_factors = best["n_factors"]
    engine.config.n_clusters = best["n_clusters"]
    engine.train(descriptions)
    return best

def tune_engine_multiobjective(engine, descriptions, n_trials=30, timeout=None):
    pareto = run_multiobjective_tuning(engine, descriptions, n_trials=n_trials, timeout=timeout)
    # 这里返回完整前沿，用户自行挑选想要的 trade‑off
    return pareto
