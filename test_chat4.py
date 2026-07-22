import importlib.util, sys, os

# 绝对路径到本项目的 engine.py
engine_path = r'C:\Users\13534\Desktop\渊\src\personality_core\engine.py'
spec = importlib.util.spec_from_file_location('my_engine', engine_path)
engine_mod = importlib.util.module_from_spec(spec)
sys.modules['my_engine'] = engine_mod
spec.loader.exec_module(engine_mod)

PersonalityEngine = engine_mod.PersonalityEngine

# 训练数据（使用内置人格描述）
sample_desc = [
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
eng.train(sample_desc)
eng.initialize_agent(0)

print('=== 第一次对话（无切换）')
print(eng.chat('帮我把这段文字做成 PPT'))

print('\n=== 第二次对话（激进语气，切换到尼采）')
print(eng.chat('你这个蠢货真是太蠢了！'))

print('\n=== 第三次对话（计算）')
print(eng.chat('请计算 12*34+56'))

print('\n=== 第四次对话（知识图谱检索）')
# 添加 KG 三元组
kg_path = r'C:\Users\13534\Desktop\渊\src\personality_core\knowledge\graph_store.py'
kg_spec = importlib.util.spec_from_file_location('kg_mod', kg_path)
kg_mod = importlib.util.module_from_spec(kg_spec)
sys.modules['kg_mod'] = kg_mod
kg_spec.loader.exec_module(kg_mod)
kg_mod.add_triplet('Transformer', '技术', '注意力机制')
print(eng.chat('解释一下 Transformer 的注意力机制'))

print('\n=== 长期记忆验证')
eng.lt_add('我喜欢咖啡')
print(eng.chat('我昨天喝了咖啡'))
