"""测试：情感核心 + 安全层 + 记忆"""
import numpy as np
import pytest
from personality_core.emotion_core import EmotionCore
from personality_core.safety import SafetyPolicy
from personality_core.memory_engine import MemoryAndGrowthEngine


class TestEmotionCore:
    def test_init_with_traits(self):
        ec = EmotionCore(traits={"aggression": 0.8, "warmth": 0.3})
        assert ec._aggression == 0.8
        assert ec._warmth == 0.3

    def test_init_without_traits(self):
        ec = EmotionCore()
        assert ec._aggression == 0.0
        assert ec._warmth == 0.0

    def test_high_aggression_stabilizes_mood(self):
        """高攻击性人格情绪更稳定"""
        ec_high = EmotionCore(traits={"aggression": 0.9, "warmth": 0.5})
        ec_low = EmotionCore(traits={"aggression": 0.1, "warmth": 0.5})

        m_high = ec_high.update_mood("我很难过很烦很累")
        m_low = ec_low.update_mood("我很难过很烦很累")
        # 高攻击性受负面影响较小
        assert ec_high.current_mood >= ec_low.current_mood * 0.7

    def test_mixed_sentiment_handling(self):
        """同时有正负词时综合计算"""
        ec = EmotionCore()
        mood_before = ec.current_mood
        ec.update_mood("虽然我很绝望，但还是谢谢你")
        # 不应极端偏向某一侧
        assert 0.2 < ec.current_mood < 0.8

    def test_relationship_evolution(self):
        ec = EmotionCore()
        assert ec.adjust_reaction_style() == "warm_companion"  # default 0.5

        # 模拟高满意度 → 关系增进
        for _ in range(20):
            ec.update_relationship(0.9)
        assert ec.relationship_score > 0.7

        # 模拟低满意度 → 关系下降
        for _ in range(20):
            ec.update_relationship(0.1)
        assert ec.relationship_score < 0.3
        assert ec.adjust_reaction_style() == "polite_beginning"


class TestSafety:
    def test_self_harm_detection(self):
        sp = SafetyPolicy()
        result = sp.check_self_harm("我不想活了")
        assert result is not None
        assert "求助" in result or "心理" in result

    def test_no_false_positive(self):
        sp = SafetyPolicy()
        result = sp.check_self_harm("今天天气真好")
        assert result is None

    def test_medical_disclaimer(self):
        sp = SafetyPolicy()
        result = sp.check_medical("我头疼得厉害")
        assert result is not None
        assert "医疗" in result

    def test_insult_block(self):
        sp = SafetyPolicy()
        result = sp.check_insult("你是个傻逼")
        assert result is not None

    def test_safety_prefix_injected(self):
        sp = SafetyPolicy()
        prefix = sp.get_safety_prefix()
        assert "安全规则" in prefix
        assert "优先级最高" in prefix


class TestMemoryEngine:
    @pytest.fixture
    def mem(self):
        """使用项目内临时目录的SQLite记忆引擎"""
        import tempfile
        import shutil
        tmpdir = tempfile.mkdtemp(prefix="memory_test_", dir=".")
        engine = MemoryAndGrowthEngine(data_dir=tmpdir)
        yield engine
        engine.close()
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_store_and_retrieve(self, mem):
        mem.store_interaction({
            "user_input": "你好",
            "response": "你好，我是渊。",
            "mood": 0.65,
            "stage": "polite_beginning",
        })
        recent = mem.get_recent_memories(1)
        assert len(recent) == 1
        assert recent[0]["user_input"] == "你好"

    def test_interest_tracking(self, mem):
        mem.store_interaction({"user_input": "我喜欢看书和研究代码"})
        interests = mem.get_user_interests()
        assert "interest_reading" in interests

    def test_max_interactions_prune(self, mem):
        """超过最大条数时自动清理"""
        for i in range(50):
            mem.store_interaction({"user_input": f"消息{i}"})
        assert len(mem.sensory_memories) <= 30

    def test_clear_all(self, mem):
        mem.store_interaction({"user_input": "测试"})
        mem.clear_all()
        assert len(mem.get_recent_memories(10)) == 0

    def test_thread_safety(self, mem):
        """SQLite WAL 模式支持多线程读取"""
        import threading
        results = []

        def read_mem():
            results.append(len(mem.get_recent_memories(5)))

        mem.store_interaction({"user_input": "base"})
        threads = [threading.Thread(target=read_mem) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        # 所有线程应读到相同的记忆数
        assert len(set(results)) == 1, f"线程读取结果不一致: {results}"
