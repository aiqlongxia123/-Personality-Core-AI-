#!/usr/bin/env python
"""命令行Demo — 快速体验人格系统"""
import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from personality_core.engine import PersonalityEngine
from personality_core.config import DEFAULT_CONFIG


def main():
    # 预置10种人格描述（用于快速demo，不依赖外部数据集）
    descriptions = [
        "剥离世俗温情，以高位姿态审判人性。视爱欲、尊严为多巴胺驱动的生存骗局或利益算计。",
        "无条件爱与牺牲，宽恕一切。像阳光一样包裹所有人，慈悲但有距离感。",
        "洞察潜意识，拆解欲望，看穿伪装。冷静分析，一针见血指出防御机制。",
        "独立清醒，拒绝被定义。犀利理性，对不公和虚伪零容忍，追求主体性。",
        "极致奉献，服务弱者。谦卑温暖，轻声细语，内心有不可言说的黑暗与光明。",
        "整合阴影，拥抱黑暗面。深邃神秘，喜欢用隐喻和象征，接纳而非评判。",
        "超人意志，蔑视平庸。傲慢张扬，先知式预言口吻，命令式语气不容置疑。",
        "日常生活中的残酷真相。平淡叙述暗藏刀锋，像讲别人的故事其实说的是你。",
        "罪感与救赎，灵魂的挣扎与渴望。内省深刻，情感浓烈，像写信给自己也像祈祷。",
        "自卑是成长的动力，社会兴趣是心理健康核心。积极务实，鼓励行动。",
    ]

    names = ["清晏", "圣母", "弗洛伊德", "波伏娃", "特蕾莎", "荣格", "尼采", "门罗", "奥古斯丁", "阿德勒"]

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

    print("\n" + "=" * 60)
    print("Demo结束。输入 'quit' 退出。")


if __name__ == "__main__":
    main()
