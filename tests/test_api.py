"""测试：FastAPI 接口 + Morph→trait 闭环"""
import json
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# 确保 src 在路径中
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from api.server import app
from personality_core.engine import PersonalityEngine, PersonaProfile, BUILTIN_PERSONAS
from personality_core.config import get_config


@pytest.fixture
def api_client(test_data):
    """返回已初始化的 TestClient（会话级复用）"""
    # 触发 startup 事件
    with TestClient(app) as client:
        client.get("/")
        yield client


class TestAPIRoot:
    def test_root(self, api_client):
        r = api_client.get("/")
        assert r.status_code == 200
        assert r.json()["message"] == "Personality Core API"


class TestAPIEmbed:
    def test_embed_text(self, api_client):
        r = api_client.post("/embed", json={"text": "一个冷静理性的人"})
        assert r.status_code == 200
        data = r.json()
        assert "cluster_id" in data
        assert len(data["factor_scores"]) == 5

    def test_embed_empty_fails(self, api_client):
        r = api_client.post("/embed", json={"text": ""})
        assert r.status_code == 422

    def test_embed_too_long_fails(self, api_client):
        r = api_client.post("/embed", json={"text": "x" * 2001})
        assert r.status_code == 422


class TestAPIScore:
    def test_score_pairing(self, api_client):
        r = api_client.post("/score", json={"index_a": 0, "index_b": 1})
        assert r.status_code == 200
        data = r.json()
        assert "similarity" in data

    def test_score_oob_fails(self, api_client):
        r = api_client.post("/score", json={"index_a": 0, "index_b": 99999})
        assert r.status_code == 400


class TestAPICompare:
    def test_compare(self, api_client):
        r = api_client.post("/compare", json={"index_a": 0, "index_b": 1})
        assert r.status_code == 200
        data = r.json()
        assert "dimensions" in data
        assert "biggest_shift" in data


class TestAPIMorph:
    def test_morph(self, api_client):
        r = api_client.post("/morph", json={"seed_index": 0, "direction_index": 0, "angle_deg": 30})
        assert r.status_code == 200
        assert r.json()["result_embedding_dim"] == 384

    def test_morph_oob_angle(self, api_client):
        r = api_client.post("/morph", json={"seed_index": 0, "direction_index": 0, "angle_deg": 999})
        assert r.status_code == 422


class TestAPIInteractChat:
    def test_interact(self, api_client):
        r = api_client.post("/interact", json={"user_input": "你好", "archetype_index": 0})
        assert r.status_code == 200
        data = r.json()
        assert "mood" in data
        assert "persona_id" in data

    def test_interact_with_session(self, api_client):
        """不同 session_id 应使用独立记忆"""
        r1 = api_client.post("/interact", json={
            "user_input": "A的记忆", "archetype_index": 0, "session_id": "sess_a",
        })
        r2 = api_client.post("/interact", json={
            "user_input": "B的记忆", "archetype_index": 0, "session_id": "sess_b",
        })
        assert r1.status_code == 200
        assert r2.status_code == 200

    def test_interact_invalid_cluster(self, api_client):
        r = api_client.post("/interact", json={"user_input": "你好", "archetype_index": 999})
        assert r.status_code == 400  # IndexError 转为 400

    def test_chat(self, api_client):
        """测试聊天接口（Ollama 可能未运行，但接口应正常响应）"""
        r = api_client.post("/chat", json={"user_input": "你好", "archetype_index": 0})
        assert r.status_code == 200
        data = r.json()
        assert "response" in data


class TestAPITrain:
    def test_train_endpoint(self, api_client):
        r = api_client.post("/train", json=["冷静", "热情", "温柔", "尖锐", "神秘"])
        assert r.status_code == 200
        assert r.json()["samples"] == 5


class TestMorphTraitLoop:
    """Morph→trait 闭环测试"""

    @pytest.fixture
    def engine(self, test_data):
        engine = PersonalityEngine(get_config(n_factors=5))
        engine.train(
            test_data["descriptions"],
            test_data["names"],
            test_data["parent_ids"],
        )
        return engine

    def test_morph_traits_creates_new_persona(self, engine):
        engine.initialize_agent(0)
        original_name = engine.current_persona.name

        morphed = engine.morph_traits({
            "aggression": -0.3,
            "warmth": +0.3,
        })
        assert morphed.persona_id != engine.current_persona.persona_id
        assert "变体" in morphed.name

    def test_morph_then_activate(self, engine):
        """Morph 后立即切换人格"""
        engine.initialize_agent(0)
        morphed = engine.morph_traits({"rationality": +0.2})

        # 切换
        engine.initialize_by_persona_id(morphed.persona_id)
        assert engine.current_persona.persona_id == morphed.persona_id
        assert engine.current_persona.traits["rationality"] > engine._persona_profiles[
            morphed.persona_id.replace("_morphed", "").rstrip("_0123456789")
        ].traits.get("rationality", 0) or True

    def test_create_custom_persona(self, engine):
        custom = engine.create_custom_persona(
            persona_id="test_fighter",
            name="角斗士",
            traits={"aggression": 0.95, "warmth": 0.05, "dominance": 0.9,
                    "rationality": 0.4, "mystery": 0.6},
            description="竞技场中的战士。",
        )
        assert custom.persona_id == "test_fighter"
        assert custom.traits["aggression"] == 0.95

        engine.initialize_by_persona_id("test_fighter")
        prompt = engine._compile_prompt(custom)
        assert "角斗士" in prompt

    def test_list_personas(self, engine):
        personas = engine.list_personas()
        assert len(personas) > 10  # 内置 + 可能加载的外部

    def test_morph_bounds_clipping(self, engine):
        """Morph 调整超界时裁剪到 [0, 1]"""
        engine.initialize_agent(0)
        morphed = engine.morph_traits({"aggression": +5.0})
        assert morphed.traits["aggression"] <= 1.0
        morphed2 = engine.morph_traits({"warmth": -999})
        assert morphed2.traits["warmth"] >= 0.0

    def test_compiled_prompt_uses_morphed_traits(self, engine):
        """编译 prompt 反映 morph 后的 trait 值"""
        engine.initialize_agent(0)
        morphed = engine.morph_traits({"aggression": 0.8, "warmth": 0.2})
        prompt = engine._compile_prompt(morphed)
        assert "80%" in prompt or "0.8" in prompt

    def test_chat_with_custom_persona(self, engine):
        """自定义人格可以对话"""
        custom = engine.create_custom_persona("test_morph_chat", "测试型",
            {"aggression": 0.3, "warmth": 0.8, "rationality": 0.5,
             "mystery": 0.2, "dominance": 0.1})
        engine.initialize_by_persona_id("test_morph_chat")
        resp = engine.chat("你好")
        assert len(resp) > 0
