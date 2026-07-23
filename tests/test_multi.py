import sys, os, json
src_path = r'C:\Users\13534\Desktop\渊\src'
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from personality_core.engine import PersonalityEngine
from personality_core.engine_tuner import attach_tuner, attach_multiobjective_tuner
from personality_core.extra_objectives import inference_latency, gpu_memory_usage

# 示例描述列表（与之前保持一致）
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

# 初始化引擎并训练一次（保证有模型）
eng = PersonalityEngine()
eng.train(descriptions)
eng.initialize_agent(0)

# 挂载调参功能
attach_tuner(eng)
attach_multiobjective_tuner(eng)

# 可选的自定义奖励函数（演示），这里使用默认的 👍/👎 简易奖励
# 直接调用多目标调参（加入额外目标）
pareto = eng.tune_hyperparameters_multi_extended(
    descriptions,
    n_trials=20,            # 为演示加快，可调大一些
    reward_fn=None,        # 使用默认奖励（👍/👎）
    extra_objectives=[inference_latency, gpu_memory_usage],
    pareto_path=r'C:\Users\13534\Desktop\渊\pareto_front_test.json'
)

print("\n=== Pareto 前沿（已写入 JSON）===")
for p in pareto:
    print(p)

# 读取并打印 JSON 文件以确认写入成功
with open(r'C:\Users\13534\Desktop\渊\pareto_front_test.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print("\nJSON 文件内容（前 3 条）:")
print(json.dumps(data[:3], ensure_ascii=False, indent=2))
