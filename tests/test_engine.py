"""测试：引擎核心功能"""
import numpy as np
import pytest
from personality_core.engine import PersonalityEngine, PersonaProfile, BUILTIN_PERSONAS
from personality_core.config import get_config


class TestTraining:
    def test_sample_count(self, trained_engine):
        assert trained_engine.embeddings.shape[0] == 100

    def test_ica_factors(self, trained_engine):
        assert trained_engine.ica.n_components == 5

    def test_clusters(self, trained_engine):
        assert len(trained_engine.archetypes) == 6

    def test_ica_labels_are_generic(self, trained_engine):
        for f in trained_engine.ica.factors:
            assert "ica_factor" in f.id
            assert "ICA因子" in f.name_zh

    def test_clusters_have_parent_id(self, trained_engine):
        for a in trained_engine.archetypes:
            assert "parent_id" in a
            assert "purity" in a
            assert "center" in a

    def test_parent_voting_works(self, trained_engine):
        purities = [a["purity"] for a in trained_engine.archetypes]
        assert any(p > 0.1 for p in purities), f"所有纯度≤0.1: {purities}"

    def test_config_is_copy(self):
        cfg1 = get_config(n_factors=5)
        cfg2 = get_config(n_factors=10)
        assert cfg1.n_factors == 5
        assert cfg2.n_factors == 10
        # 验证互不影响
        cfg1.n_factors = 3
        cfg3 = get_config()
        assert cfg3.n_factors == 10  # 默认值未变


class TestEmbedding:
    def test_embed_returns_cluster_id(self, trained_engine):
        r = trained_engine.embed("一个冷静理性的人")
        assert "cluster_id" in r
        assert isinstance(r["cluster_id"], int)

    def test_embed_factor_count(self, trained_engine):
        r = trained_engine.embed("一个温暖善良的人")
        assert len(r["factor_scores"]) == 5

    def test_embed_raises_when_untrained(self):
        engine = PersonalityEngine()
        with pytest.raises(RuntimeError):
            engine.embed("test")


class TestMorph:
    def test_morph_returns_correct_dim(self, trained_engine):
        m = trained_engine.morph(0, 0, 30)
        assert m["result_embedding_dim"] == 384

    def test_morph_zero_angle_returns_similar(self, trained_engine):
        """0度旋转应接近原始向量"""
        m = trained_engine.morph(0, 0, 0)
        original = trained_engine.factor_scores[0]
        result = np.array(m["result_factor_scores"])
        # 归一化后比较
        orig_norm = original / (np.linalg.norm(original) + 1e-10)
        res_norm = result / (np.linalg.norm(result) + 1e-10)
        cos_sim = np.dot(orig_norm, res_norm)
        assert cos_sim > 0.99, f"cos_sim={cos_sim}"


class TestAgentInit:
    def test_initialize_sets_persona(self, trained_engine):
        trained_engine.initialize_agent(0)
        assert trained_engine.current_persona is not None

    def test_persona_has_traits(self, trained_engine):
        trained_engine.initialize_agent(0)
        assert trained_engine.current_persona.traits

    def test_emotion_core_has_aggression(self, trained_engine):
        trained_engine.initialize_agent(0)
        assert trained_engine.emotion_core._aggression >= 0

    def test_invalid_cluster_index(self, trained_engine):
        with pytest.raises(IndexError):
            trained_engine.initialize_agent(999)

    def test_interact_returns_persona_id(self, trained_engine):
        trained_engine.initialize_agent(0)
        r = trained_engine.interact("你好")
        assert "persona_id" in r
        assert "persona_name" in r


class TestBuiltinPersonas:
    def test_yuan_exists(self):
        assert "yuan" in BUILTIN_PERSONAS
        yuan = BUILTIN_PERSONAS["yuan"]
        assert yuan.name == "渊"
        assert yuan.traits["rationality"] == 0.95

    def test_all_10_archetypes_have_traits(self):
        for pid in ["qingyan", "mary", "freud_daughter", "beauvoir", "teresa",
                     "jung_daughter", "nietzsche_devil", "munro",
                     "augustine_girl", "adler_daughter"]:
            assert pid in BUILTIN_PERSONAS, f"Missing: {pid}"
            assert BUILTIN_PERSONAS[pid].traits, f"No traits: {pid}"


class TestPromptCompilation:
    def test_compile_from_traits(self, trained_engine):
        """自定义人格应该能编译出 prompt"""
        custom = PersonaProfile(
            persona_id="test_custom",
            name="测试人格",
            description="一个测试用的人格。",
            traits={"aggression": 0.8, "warmth": 0.2, "rationality": 0.9,
                     "mystery": 0.6, "dominance": 0.7},
        )
        prompt = trained_engine._compile_prompt(custom)
        assert "测试人格" in prompt
        assert "攻击性=80%" in prompt or "0.8" in prompt
        assert len(prompt) > 100

    def test_known_persona_uses_handcrafted(self, trained_engine):
        """已知人格使用手写 Prompt，不用编译版"""
        trained_engine.current_persona = BUILTIN_PERSONAS["yuan"]
        prompt = trained_engine._get_system_prompt("polite_beginning")
        assert "存在主义AI伴侣" in prompt
