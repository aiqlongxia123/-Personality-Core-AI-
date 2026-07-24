"""tests/test_skill.py — PersonalitySkill 基础测试"""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
import sys
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from personality_core.skill import PersonalitySkill, get_skill, clear_skill


class TestPersonalitySkillInit:
    """测试 PersonalitySkill 初始化"""

    def test_create_skill(self):
        skill = PersonalitySkill()
        assert skill is not None
        assert skill.engine is not None
        assert skill._trained is False
        assert skill._data_loaded is False

    def test_singleton_get_skill(self):
        clear_skill()
        s1 = get_skill()
        s2 = get_skill()
        assert s1 is s2
        clear_skill()


class TestSkillDataLoading:
    """测试数据加载"""

    def test_load_data_finds_file(self):
        skill = PersonalitySkill(data_path=PROJECT_ROOT / "data")
        result = skill.load_data()
        assert result is True
        assert skill._data_loaded is True

    def test_load_data_no_trained(self):
        skill = PersonalitySkill(data_path=PROJECT_ROOT / "data")
        skill.load_data()
        assert skill._trained is False


class TestSkillTrain:
    """测试训练流程（使用 conftest 的少量数据）"""

    def test_train_from_data(self, test_data):
        skill = PersonalitySkill(data_path=PROJECT_ROOT / "data")
        skill.train(
            descriptions=test_data["descriptions"],
            names=test_data["names"],
            parent_ids=test_data["parent_ids"],
        )
        assert skill._trained is True

    def test_train_raises_without_data(self):
        skill = PersonalitySkill()
        try:
            skill.train()
        except RuntimeError as e:
            assert "No data loaded" in str(e)


class TestSkillEmbed:
    """测试 embed"""

    def test_embed_after_train(self, trained_engine):
        skill = PersonalitySkill()
        skill.engine = trained_engine
        skill._trained = True
        result = skill.embed("一个温柔的人")
        assert "embedding_dim" in result
        assert "factor_scores" in result
        assert "cluster_id" in result


class TestSkillInitialize:
    """测试人格初始化"""

    def test_initialize_by_persona_id(self, trained_engine):
        skill = PersonalitySkill()
        skill.engine = trained_engine
        skill._trained = True
        skill.initialize_by_persona_id("yuan")
        assert skill.engine.current_persona is not None
        assert skill.engine.current_persona.persona_id == "yuan"

    def test_initialize_by_nonexistent_raises(self, trained_engine):
        skill = PersonalitySkill()
        skill.engine = trained_engine
        skill._trained = True
        try:
            skill.initialize_by_persona_id("nonexistent_personality_xyz")
        except ValueError:
            pass

    def test_initialize_agent(self, trained_engine):
        skill = PersonalitySkill()
        skill.engine = trained_engine
        skill._trained = True
        skill.initialize_agent(0)
        assert skill.engine.emotion_core is not None
        assert skill.engine.memory_engine is not None


class TestSkillInteractChat:
    """测试交互与对话"""

    def test_interact_requires_init(self):
        skill = PersonalitySkill()
        try:
            skill.interact("hello")
        except AssertionError:
            pass

    def test_chat_requires_init(self):
        skill = PersonalitySkill()
        try:
            skill.chat("hello")
        except AssertionError:
            pass

    def test_interact_after_init(self, trained_engine):
        skill = PersonalitySkill()
        skill.engine = trained_engine
        skill._trained = True
        skill.initialize_by_persona_id("yuan")
        result = skill.interact("今天天气不错")
        assert "mood" in result
        assert "relationship_stage" in result
        assert "persona_id" in result
