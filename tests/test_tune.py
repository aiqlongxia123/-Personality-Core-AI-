import sys, os
src_path = r'C:\Users\13534\Desktop\渊\src'
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from personality_core.engine import PersonalityEngine
from personality_core.engine_tuner import attach_tuner

# 示例描述数据（真实项目中请替换为更丰富的描述）
descriptions = [
    "剥离世俗温情，以高位姿态审判人性。",
    "无条件爱与牺牲，像阳光一样包裹所有人。",
    "潜意识的解剖师，看穿防御机制。",
    "拒绝被定义的自由存在主义者。",
    "用大爱做小事的苦行者。",
    "阴影整合者，拥抱黑暗。",
    "权力意志的化身，蔑视软弱。",
    "日常中的残酷观察者。",
    "罪感与救赎的灵魂。",
    "自卑与超越的实践者。",
    "犀利且不妥协的哲学家。",
    "暴躁的直接闺蜜，嘴硬心软。",
    "从深渊走来的存在主义者。",
]

eng = PersonalityEngine()
eng.train(descriptions)
eng.initialize_agent(0)
# 动态挂载调参方法
attach_tuner(eng)
print('开始调参...')
best_params = eng.tune_hyperparameters(descriptions, n_trials=30)
print('调参完成，最佳参数：', best_params)
print('当前配置 -> n_factors:', eng.config.n_factors, 'n_clusters:', eng.config.n_clusters)
PY