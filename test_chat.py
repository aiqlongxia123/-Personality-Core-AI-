import sys, os
sys.path.append(r'C:\Users\13534\Desktop\渊\src')
from personality_core.engine import PersonalityEngine

eng = PersonalityEngine()
eng.initialize_agent(0)
print('=== 第一次对话（无切换）')
print(eng.chat('帮我把这段文字做成 PPT'))

print('\n=== 第二次对话（激进语气，切换到尼采)')
print(eng.chat('你这个蠢货真是太蠢了！'))

print('\n=== 第三次对话（计算）')
print(eng.chat('请计算 12*34+56'))

print('\n=== 第四次对话（知识图谱检索）')
# 先插入一个 KG 三元组
from personality_core.knowledge.graph_store import add_triplet
add_triplet('Transformer', '技术', '注意力机制')
print(eng.chat('解释一下 Transformer 的注意力机制'))

print('\n=== 长期记忆验证')
eng.lt_add('我喜欢咖啡')
print(eng.chat('我昨天喝了咖啡'))
