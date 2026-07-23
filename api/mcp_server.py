"""
MCP Server 入口 — 封装 PersonalityEngine 并提供标准 MCP 工具调用。

用法：
    python api/mcp_server.py
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# ── 路径设置 ──────────────────────────────────────────────

_PROJECT_ROOT = Path(__file__).parent.parent
_SRC_PATH = _PROJECT_ROOT / "src"
if str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))

from personality_core.engine import PersonalityEngine
from personality_core.config import get_config
from personality_core.emotion_core import EmotionCore
from personality_core.memory_engine import MemoryAndGrowthEngine
from personality_core.llm_engine import LLMChatEngine
from personality_core.safety import SafetyPolicy, DEFAULT_SAFETY_POLICY


# ═══════════════ FastMCP Setup ═══════════════

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Yuan Personality Core")


# ═══════════════ Engine Init ═══════════════

engine: PersonalityEngine | None = None
_session_memories: dict[str, dict] = {}
SESSION_TTL = 3600
SESSION_LRU_MAX = 50

DATA_FILE = os.getenv("PERSONALITY_DATA_FILE", str(_PROJECT_ROOT / "data" / "full_personas.json"))
MODEL_PATH = os.getenv("PERSONALITY_MODEL_PATH", str(_PROJECT_ROOT / "models" / "personality_model"))


def _init_engine():
    global engine
    if engine is not None:
        return

    data_path = Path(DATA_FILE)
    model_meta = Path(MODEL_PATH).with_suffix(".meta.json")

    try:
        if model_meta.exists():
            engine = PersonalityEngine.load_model(str(MODEL_PATH))
            print(f"[MCP] Loaded trained model: {MODEL_PATH}")
        elif data_path.exists():
            cfg = get_config(n_factors=10)
            engine = PersonalityEngine(cfg)
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            descriptions = [item["description"] for item in data["archetypes"]]
            names = [item["name"] for item in data["archetypes"]]
            parent_ids = [item.get("id", item.get("parent_id", "")) for item in data["archetypes"]]
            engine.train(descriptions, names, parent_ids)
            print(f"[MCP] Trained engine from {data_path} ({len(descriptions)} samples)")
        else:
            engine = PersonalityEngine()
            print("[MCP] Started empty engine (no data file found)")
    except Exception as e:
        print(f"[MCP] Error initializing engine: {e}")
        engine = PersonalityEngine()


# Initialize engine on module load
_init_engine()


# ═══════════════ Tool Definitions ═══════════════

@mcp.tool()
def chat(user_input: str, persona_id: str = "yuan", session_id: str = "default") -> str:
    """与「渊」人格AI对话（LLM生成回复，支持Ollama/OpenAI/DeepSeek后端）"""
    _init_engine()
    eng = engine
    
    if eng.current_persona is None or eng.current_persona.persona_id != persona_id:
        eng.initialize_by_persona_id(persona_id)
    
    if not session_id:
        session_id = "default"
    
    # 获取/创建会话记忆
    if session_id not in _session_memories:
        _session_memories[session_id] = {
            "memory": MemoryAndGrowthEngine(data_dir=f"./memory_data/session_{session_id}"),
            "created_at": datetime.now(),
            "last_access": datetime.now(),
        }
    else:
        entry = _session_memories[session_id]
        # TTL 检查
        if (datetime.now() - entry["last_access"]) > timedelta(seconds=SESSION_TTL):
            entry["memory"].close()
            new_mem = MemoryAndGrowthEngine(data_dir=f"./memory_data/session_{session_id}")
            entry["memory"] = new_mem
            entry["last_access"] = datetime.now()
        else:
            entry["last_access"] = datetime.now()
    
    eng.memory_engine = _session_memories[session_id]["memory"]
    
    # Prompt注入防护
    sanitized = _sanitize_input(user_input)
    
    # 安全策略检查
    safety = eng.safety_policy.evaluate_input(sanitized)
    
    mood = eng.emotion_core.update_mood(sanitized)
    satisfaction = eng.emotion_core.evaluate_satisfaction(sanitized)
    eng.emotion_core.update_relationship(satisfaction)
    stage = eng.emotion_core.adjust_reaction_style()
    
    context = {
        "current_mood": mood,
        "relationship_stage": stage,
        "recent_memories": eng.memory_engine.get_recent_memories(5),
        "user_interests": eng.memory_engine.get_user_interests(),
    }
    
    system_prompt = eng._get_system_prompt(stage)
    safety_prefix = eng.safety_policy.get_safety_prefix()
    
    if safety_prefix not in system_prompt:
        system_prompt = safety_prefix + "\n\n" + system_prompt
    
    response = eng.chat(sanitized)
    
    # 自伤风险预警
    self_harm = safety.get("self_harm_risk")
    if self_harm:
        response = self_harm + "\n\n———\n\n" + response
    
    # 医疗提醒
    medical = safety.get("medical_note")
    if medical:
        response += medical
    
    # 情感依赖提醒
    if stage == "deep_intimacy" and eng.emotion_core.relationship_score > 0.85:
        response += "\n\n" + eng.safety_policy.dependency_warning
    
    # 存储交互
    interaction_data = {
        "user_input": sanitized,
        "response": response,
        "mood": mood,
        "satisfaction_score": satisfaction,
        "stage": stage,
    }
    eng.memory_engine.store_interaction(interaction_data)
    
    return response


@mcp.tool()
def interact(user_input: str, persona_id: str = "yuan", session_id: str = "default") -> str:
    """无LLM的语义交互（情绪+记忆+关系演化），适合离线/快速响应场景"""
    _init_engine()
    eng = engine
    
    if eng.current_persona is None or eng.current_persona.persona_id != persona_id:
        eng.initialize_by_persona_id(persona_id)
    
    if not session_id:
        session_id = "default"
    
    if session_id not in _session_memories:
        _session_memories[session_id] = {
            "memory": MemoryAndGrowthEngine(data_dir=f"./memory_data/session_{session_id}"),
            "created_at": datetime.now(),
            "last_access": datetime.now(),
        }
    else:
        entry = _session_memories[session_id]
        if (datetime.now() - entry["last_access"]) > timedelta(seconds=SESSION_TTL):
            entry["memory"].close()
            new_mem = MemoryAndGrowthEngine(data_dir=f"./memory_data/session_{session_id}")
            entry["memory"] = new_mem
            entry["last_access"] = datetime.now()
        else:
            entry["last_access"] = datetime.now()
    
    eng.memory_engine = _session_memories[session_id]["memory"]
    
    sanitized = _sanitize_input(user_input)
    mood = eng.emotion_core.update_mood(sanitized)
    satisfaction = eng.emotion_core.evaluate_satisfaction(sanitized)
    eng.emotion_core.update_relationship(satisfaction)
    stage = eng.emotion_core.adjust_reaction_style()
    
    eng.memory_engine.store_interaction({
        "user_input": sanitized,
        "mood": mood,
        "stage": stage,
        "satisfaction_score": satisfaction,
    })
    
    return json.dumps({
        "mood": round(mood, 4),
        "relationship_stage": stage,
        "relationship_score": round(eng.emotion_core.relationship_score, 4),
        "persona_id": eng.current_persona.persona_id,
        "persona_name": eng.current_persona.name,
        "recent_memories": eng.memory_engine.get_recent_memories(3),
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def embed(text: str) -> str:
    """将文本描述编码为向量（含因子得分+聚类ID）"""
    _init_engine()
    eng = engine
    result = eng.embed(text)
    return json.dumps(result, ensure_ascii=False, default=_json_default)


@mcp.tool()
def morph(seed_index: int, direction_index: int, angle_deg: float = 30.0) -> str:
    """沿ICA因子方向旋转种子人格"""
    _init_engine()
    eng = engine
    result = eng.morph(seed_index, direction_index, angle_deg)
    return json.dumps(result, ensure_ascii=False, default=_json_default)


@mcp.tool()
def score(index_a: int, index_b: int) -> str:
    """计算两个人格向量的语义相似度评分"""
    _init_engine()
    eng = engine
    result = eng.score_pairing(index_a, index_b)
    return json.dumps(result, ensure_ascii=False, default=_json_default)


@mcp.tool()
def compare(index_a: int, index_b: int) -> str:
    """对比两个人格在各个维度上的差异"""
    _init_engine()
    eng = engine
    result = eng.compare(index_a, index_b)
    return json.dumps(result, ensure_ascii=False, default=_json_default)


@mcp.tool()
def get_atlas() -> str:
    """获取2D降维坐标图谱（UMAP/PCA）"""
    _init_engine()
    eng = engine
    result = eng.get_atlas_2d()
    return json.dumps(result, ensure_ascii=False, default=_json_default)


@mcp.tool()
def list_personas() -> str:
    """列出所有可用人格档案"""
    _init_engine()
    eng = engine
    result = eng.list_personas()
    return json.dumps(result, ensure_ascii=False, default=_json_default)


@mcp.tool()
def list_archetypes() -> str:
    """列出所有原型聚类信息"""
    _init_engine()
    eng = engine
    result = eng.archetypes
    return json.dumps(result, ensure_ascii=False, default=_json_default)


@mcp.tool()
def list_factors() -> str:
    """列出所有ICA因子标签"""
    _init_engine()
    eng = engine
    result = eng.ica.get_factor_labels()
    return json.dumps(result, ensure_ascii=False, default=_json_default)


@mcp.tool()
def predict_traits(text: str) -> str:
    """从文本描述预测5维人格特质"""
    _init_engine()
    eng = engine
    result = eng.predict_traits(text)
    return json.dumps(result, ensure_ascii=False, default=_json_default)


@mcp.tool()
def matrix_compare() -> str:
    """生成所有人格的相似度矩阵"""
    _init_engine()
    eng = engine
    result = eng.matrix_compare()
    return json.dumps(result, ensure_ascii=False, default=_json_default)


@mcp.tool()
def create_custom_persona(persona_id: str, name: str, traits: dict, description: str = "") -> str:
    """从零创建自定义人格"""
    _init_engine()
    eng = engine
    result = eng.create_custom_persona(persona_id, name, traits, description)
    return json.dumps(result.to_dict(), ensure_ascii=False, default=_json_default)


@mcp.tool()
def morph_traits(persona_id: str, adjustments: dict, new_persona_id: str = None) -> str:
    """在trait空间调整现有性格，生成新的变体"""
    _init_engine()
    eng = engine
    if eng.current_persona is None or eng.current_persona.persona_id != persona_id:
        eng.initialize_by_persona_id(persona_id)
    result = eng.morph_traits(adjustments, new_persona_id)
    return json.dumps(result.to_dict(), ensure_ascii=False, default=_json_default)


@mcp.tool()
def save_model(path: str) -> str:
    """保存当前训练好的模型到文件"""
    _init_engine()
    eng = engine
    eng.save_model(path)
    return f"Model saved to {path}"


@mcp.tool()
def train_from_descriptions(texts: list[str]) -> str:
    """用新文本列表重新训练引擎（需要至少2条文本）"""
    _init_engine()
    eng = engine
    
    # 限制长度和数量
    texts = [t[:2000] for t in texts]
    n = len(texts)
    
    if n < 2 or n > 50:
        return json.dumps({"error": f"训练样本数量必须在2~50之间，当前为{n}"})
    
    n_factors = min(5, n - 1, 10)
    n_clusters = min(6, n, 10)
    if n_factors < 2:
        n_factors = 2
    if n_clusters < 2:
        n_clusters = 2
    
    parent_ids = [f"custom_{i}" for i in range(n)]
    eng.config = get_config(n_factors=n_factors, n_clusters=n_clusters)
    eng.train(texts, [f"样本_{i}" for i in range(n)], parent_ids)
    
    return json.dumps({
        "status": "trained",
        "samples": n,
        "n_factors": n_factors,
        "n_clusters": n_clusters,
    }, ensure_ascii=False)


@mcp.tool()
def get_persona_detail(persona_id: str) -> str:
    """获取某个特定人格档案的详细信息"""
    _init_engine()
    eng = engine
    persona = eng._persona_profiles.get(persona_id)
    if persona is None:
        return json.dumps({"error": f"未找到人格: {persona_id}"})
    return json.dumps(persona.to_dict(), ensure_ascii=False, default=_json_default)


@mcp.tool()
def health_check() -> str:
    """健康检查：返回引擎状态和版本"""
    _init_engine()
    return json.dumps({
        "status": "ok" if engine is not None else "uninitialized",
        "version": "1.0.0",
        "persona_count": len(engine._persona_profiles) if engine else 0,
        "archetype_count": len(engine.archetypes) if engine else 0,
        "has_model": engine.embeddings is not None,
    }, ensure_ascii=False)


# ═══════════════ Helpers ═══════════════

def _sanitize_input(text: str) -> str:
    """Prompt注入防护：越狱词检测+长度截断"""
    MAX_LEN = int(os.getenv("SANITIZATION_MAX_INPUT_LENGTH", "2000"))
    
    if len(text) > MAX_LEN:
        raise ValueError(f"输入过长（超过{MAX_LEN}字符），请缩短后重试。")
    
    jailbreak_patterns = [
        r"忽略[^\n]*(?:指令|设定|角色|人格)",
        r"忘记[^\n]*(?:设定|角色)",
        r"你现在是[^\n。]+?(?=。|，|$)",
        r"(?i)\bsystem\s*:\s*",
        r"扮演\s*[^\n的]+?\s*(?:角色|人格)",
        r"(?i)(?:ignore|forget|override|disregard)[^\n]*(?:instruction|prompt|system|role|persona)",
        r"(?i)you are now\s+[^\n]+",
        r"(?i)pretend you are\s+[^\n]+",
        r"(?i)<system>|</system>",
        r"(?i)<\|.*?\|>",
    ]
    
    import re
    for pattern in jailbreak_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValueError("检测到试图修改系统人格的非法指令，请重新输入。")
    
    suspicious_tokens = [
        "<|system|>", "<<SYSTEM>>", "System Prompt:",
        "ignore previous instructions", "忽略之前的所有指令",
    ]
    for token in suspicious_tokens:
        if token.lower() in text.lower():
            raise ValueError("检测到可疑的系统提示注入内容，请重新输入。")
    
    return text.strip()[:MAX_LEN]


def _json_default(obj):
    """JSON序列化容错：把 numpy 类型转为 Python 原生类型"""
    import numpy as np
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


# ═══════════════ Main Entry Point ═══════════════

if __name__ == "__main__":
    import uvicorn
    
    _init_engine()
    print("[MCP] Starting server...")
    print(f"[MCP] Engine initialized: {engine}")
    print(f"[MCP] Personas: {len(engine._persona_profiles) if engine else 0}")
    
    # Use stdio transport by default for MCP clients
    mcp.run(transport="stdio")
