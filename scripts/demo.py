#!/usr/bin/env python
"""命令行Demo — 快速体验人格系统"""
import sys
import json
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from personality_core.engine import PersonalityEngine
from personality_core.config import DEFAULT_CONFIG


def main():
    data_path = Path(__file__).parent.parent / "data" / "archetypes_extended.json"
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    descriptions = [item["description"] for item in data["archetypes"]]
    names = [item["name"] for item in data["archetypes"]]

    print("=" * 60)
    print("  人格AI系统 v0.1 — 快速Demo")
    print("=" * 60)

    config = DEFAULT_CONFIG
    config.n_factors = 5
    engine = PersonalityEngine(config)
    engine.train(descriptions, names)

    print("\n✅ 训练完成")
    print(f"   样本数: {len(descriptions)}")
    print(f"   因子数: {config.n_factors}")
    print(f"   原型数: {config.n_clusters}")

    # 显示因子
    print("\n📊 人格因子:")
    for f in engine.ica.get_factor_labels():
        print(f"   {f['factor_index']} {f['name_zh']}: {f['pole_a']} ↔ {f['pole_b']}")

    # 显示原型
    print("\n🎭 人格原型:")
    for a in engine.archetypes:
        print(f"   {a['name']} — {a['size']}个成员")

    # 测试配对评分
    print("\n🔗 配对评分测试:")
    for i in range(min(3, len(descriptions))):
        for j in range(i+1, min(4, len(descriptions))):
            score = engine.score_pairing(i, j)
            print(f"   {names[i]} ↔ {names[j]}: {score['compatibility']:.4f} ({score['label']})")

    # 测试对比
    print("\n⚖️ 人格对比测试 (清晏 vs 圣母):")
    comp = engine.compare(0, 1)
    print(f"   最大变化维度: {comp['biggest_shift']['dimension']} → {comp['biggest_shift']['direction']}")

    # 交互式对话
    print("\n💬 开始对话 (渊)...")
    engine.initialize_agent(0)

    prompts = [
        "你好",
        "我最近很迷茫",
        "我头疼",
        "你觉得我怎么样",
    ]

    for prompt in prompts:
        result = engine.interact(prompt)
        print(f"\n你: {prompt}")
        print(f"系统状态: 情绪={result['mood']:.2f}, 阶段={result['relationship_stage']}")

    # 测试LLM对话
    print("\n🤖 测试LLM对话 (需要Ollama运行中)...")
    try:
        response = engine.chat("你好，我最近很迷茫")
        print(f"\n渊: {response}")
    except Exception as e:
        print(f"\n[LLM对话失败] {e}")
        print("提示：请确保Ollama正在运行: ollama serve")

    print("\n" + "=" * 60)
    print("Demo结束。输入 'quit' 退出。")


if __name__ == "__main__":
    main()
