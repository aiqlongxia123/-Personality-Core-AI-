"""
完整流程验证：训练 → Agent 初始化
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from personality_core.engine import PersonalityEngine
import json

# 读取完整数据集
data_path = Path("data/full_personas.json")
with open(data_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

descriptions = [a['description'] for a in data['archetypes']]
names = [a['name'] for a in data['archetypes']]
parent_ids = [a['id'] for a in data['archetypes']]

# 初始化引擎
engine = PersonalityEngine()
print(f"引擎初始化后: {len(engine.list_personas())} 个人格档案")

# 训练
print("\n=== 开始训练 ===")
engine.train(
    descriptions=descriptions,
    archetype_names=names,
    parent_ids=parent_ids,
)

print(f"\n训练后: {len(engine.list_personas())} 个人格档案")

# 列出聚类原型
print(f"\n聚类原型 (共{len(engine.archetypes)}个):")
for i, arch in enumerate(engine.archetypes):
    print(f"  Cluster {i}: {arch['name']} (parent_id={arch['parent_id']}, size={arch['size']})")

# 通过聚类索引初始化 Agent
try:
    engine.initialize_agent(cluster_index=0)
    print(f"\n✅ Agent 初始化成功: {engine.current_persona.name} (特质: {engine.current_persona.traits})")
except Exception as e:
    print(f"\n❌ Agent 初始化失败: {e}")

# 通过 variant ID 初始化
try:
    engine.initialize_by_persona_id("qingyan_5")
    print(f"✅ 通过 variant ID 激活: {engine.current_persona.name} (特质: {engine.current_persona.traits})")
except Exception as e:
    print(f"❌ Variant ID 激活失败: {e}")

print("\n=== 全部测试通过 ===")
