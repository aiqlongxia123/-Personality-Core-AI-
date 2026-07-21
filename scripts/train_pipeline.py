"""训练流水线 — 一键训练完整人格空间"""
import json
from pathlib import Path
import numpy as np

from personality_core.engine import PersonalityEngine
from personality_core.config import get_config


def load_dataset(path: str) -> tuple[list[str], list[str], list[str]]:
    """从JSON加载数据集：返回(descriptions, names, parent_ids)"""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    descriptions = [item["description"] for item in data["archetypes"]]
    names = [item["name"] for item in data["archetypes"]]
    parent_ids = [item.get("parent_id", "") for item in data["archetypes"]]
    return descriptions, names, parent_ids


def main():
    data_path = Path(__file__).parent.parent / "data" / "archetypes_extended.json"

    if not data_path.exists():
        print(f"找不到数据集: {data_path}")
        print("请先准备 archetypes.json 文件")
        return

    print(f"加载数据集: {data_path}")
    descriptions, names, parent_ids = load_dataset(str(data_path))
    print(f"共 {len(descriptions)} 个人格样本")

    engine = PersonalityEngine(get_config(n_factors=5))
    engine.train(descriptions, names, parent_ids)

    # 保存模型
    model_path = Path(__file__).parent.parent / "models" / "personality_model.json"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    engine.save_model(str(model_path))
    print(f"\n模型已保存至: {model_path}")

    # 测试交互
    engine.initialize_agent(0)
    print("\n=== 快速测试 ===")
    test_inputs = ["你好", "我最近很迷茫", "我头疼", "你觉得我怎么样"]
    for t in test_inputs:
        result = engine.interact(t)
        print(f"输入: {t}")
        print(f"情绪: {result['mood']:.2f}, 阶段: {result['relationship_stage']}")
        print()


if __name__ == "__main__":
    main()
