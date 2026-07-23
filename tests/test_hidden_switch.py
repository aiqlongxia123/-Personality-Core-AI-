import sys, os
src_path = r'C:\Users\13534\Desktop\渊\src'
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from personality_core.engine import PersonalityEngine
from personality_core.engine_tuner import attach_tuner

# 描述列表（与之前相同）
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
attach_tuner(eng)

print('初始人格:', eng.current_persona.name)

# 激进语句（含软化关键词 "糊涂"）
resp = eng.chat('我真的有点糊涂，快给我点刺激的吐槽！')
print('对话回复:', resp)
print('对话后人格:', eng.current_persona.name)

# 温柔语句（含 "谢谢"）
resp2 = eng.chat('谢谢你刚才的帮助')
print('对话回复2:', resp2)
print('对话后人格2:', eng.current_persona.name)
