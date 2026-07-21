"""pytest 配置文件 — 人格AI系统测试"""
import json
import sys
from pathlib import Path
import pytest

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))


@pytest.fixture(scope="session")
def test_data():
    """加载测试数据"""
    data_path = PROJECT_ROOT / "data" / "archetypes_extended.json"
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    return {
        "descriptions": [d["description"] for d in data["archetypes"]],
        "names": [d["name"] for d in data["archetypes"]],
        "parent_ids": [d.get("parent_id", "") for d in data["archetypes"]],
    }


@pytest.fixture(scope="session")
def trained_engine(test_data):
    """返回已训练的引擎（session级复用）"""
    from personality_core.engine import PersonalityEngine
    from personality_core.config import get_config

    engine = PersonalityEngine(get_config(n_factors=5))
    engine.train(
        test_data["descriptions"],
        test_data["names"],
        test_data["parent_ids"],
    )
    return engine
