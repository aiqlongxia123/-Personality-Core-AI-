"""
合并增强现有数据集和生成数据
"""
import json

# 读取原始完整数据集
with open('data/archetypes.json', 'r', encoding='utf-8') as f:
    original_data = json.load(f)

# 读取生成的变体数据
with open('data/expanded_personas.json', 'r', encoding='utf-8') as f:
    variants_data = json.load(f)

# 构建原始人格的映射，按parent_id关联原型
original_by_parent = {}
for orig in original_data['archetypes']:
    # 使用id去掉下划线部分来匹配variant的parent_id
    parent_id = orig['id']
    if parent_id not in original_by_parent:
        original_by_parent[parent_id] = orig

# 为variants添加对话和morph方向（如果缺乏）
enhanced_variants = []
for variant in variants_data['archetypes']:
    enhanced = variant.copy()
    # 获取原型的对话和morph方向
    parent_id = variant.get('parent_id')
    if parent_id in original_by_parent:
        parent = original_by_parent[parent_id]
        # 合并一些属性，但尽量保持variant自己的description和traits
        if 'sample_dialogue' not in enhanced or not enhanced.get('sample_dialogue'):
            enhanced['sample_dialogue'] = parent.get('sample_dialogue', [])[:2]  # 只取两个作为示例
        if 'morph_directions' not in enhanced:
            enhanced['morph_directions'] = parent.get('morph_directions', {})

    enhanced_variants.append(enhanced)

# 合并原始数据 + 增强后的变体
final_combined = {
    "archetypes": original_data['archetypes'] + enhanced_variants,
    "metadata": {
        "generated_at": "2026-07-22",
        "version": "1.0",
        "total_count": len(original_data['archetypes']) + len(enhanced_variants)
    }
}

# 保存新的完整数据集
output_path = 'data/full_personas.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(final_combined, f, ensure_ascii=False, indent=2)

print(f"合并完成！总计 {len(final_combined['archetypes'])} 个人格样本")
print(f"已保存到 {output_path}")

# 展示一些统计信息
domains = {}
for arch in final_combined['archetypes']:
    domain = arch.get('domain', 'unknown')
    domains[domain] = domains.get(domain, 0) + 1
print("\n按领域分布:")
for d, c in sorted(domains.items(), key=lambda x: -x[1]):
    print(f"  {d}: {c}")

# 显示一个完整示例
print("\n完整示例 (清晏_5):")
for arch in final_combined['archetypes']:
    if 'qingyan' in arch.get('id', '') and '_5' in arch.get('id', ''):
        print(f"ID: {arch['id']}")
        print(f"名称: {arch['name']}")
        print(f"描述: {arch['description']}")
        print(f"领域: {arch.get('domain')}")
        print(f"特质: {json.dumps(arch['traits'], ensure_ascii=False)}")
        print(f"对话: {arch['sample_dialogue'][:2]}")
        break
