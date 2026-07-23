import sys, os
src_path = r'C:\Users\13534\Desktop\渊\src'
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from personality_core.engine import PersonalityEngine
from personality_core.engine_tuner import attach_tuner, attach_multiobjective_tuner

# 示例描述（与之前相同）
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
eng.initialize_agent(0)  # 使用渊人格

# 挂载调参功能（可选）
attach_tuner(eng)
attach_multiobjective_tuner(eng)

# 简单对话演示
print('=== 对话 1（普通）')
print(eng.chat('帮我把这段文字写成 PPT'))

print('\n=== 对话 2（激进语气）')
print(eng.chat('你这蠢货怎么这么笨！'))

print('\n=== 对话 3（计算）')
print(eng.chat('请计算 23*7+5'))

print('\n=== 对话 4（知识图谱）')
from personality_core.knowledge.graph_store import add_triplet
add_triplet('Transformer', '技术', '注意力机制')
print(eng.chat('解释一下 Transformer 的注意力机制'))
