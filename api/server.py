"""FastAPI 人格AI系统接口"""
import os
import sys
from pathlib import Path

# 确保 src 在 Python 路径
_src = Path(__file__).parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from fastapi import FastAPI, HTTPException, Query, Body, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
import numpy as np
import uvicorn

from personality_core.engine import PersonalityEngine
from personality_core.config import get_config


# ═══════════════ API 鉴权 ═══════════════

API_KEY = os.getenv("PERSONALITY_API_KEY", "")
if not API_KEY:
    raise RuntimeError(
        "环境变量 PERSONALITY_API_KEY 未设置，请配置后启动服务。"
    )

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def validate_api_key(api_key: str | None = Depends(api_key_header)):
    """验证 X-API-Key 请求头"""
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API Key")
    return api_key


app = FastAPI(
    title="Personality Core API",
    description="基于向量嵌入空间的人格AI系统",
    version="0.1.1",
)

# 全局引擎实例
engine: Optional[PersonalityEngine] = None

# 简易会话隔离：session_id → MemoryAndGrowthEngine
_sessions: dict[str, "MemoryAndGrowthEngine"] = {}


def _get_or_create_session(session_id: str, engine: PersonalityEngine):
    """获取或创建会话级记忆"""
    from personality_core.memory_engine import MemoryAndGrowthEngine
    if session_id not in _sessions:
        _sessions[session_id] = MemoryAndGrowthEngine(
            data_dir=f"./memory_data/session_{session_id}"
        )
    mem = _sessions[session_id]
    engine.memory_engine = mem
    return mem


@app.on_event("startup")
async def startup():
    """启动时自动训练或加载引擎"""
    global engine
    import json
    from pathlib import Path

    data_path = Path(__file__).parent.parent / "data" / "full_personas.json"
    model_path = Path(__file__).parent.parent / "models" / "personality_model"

    try:
        if model_path.with_suffix(".meta.json").exists():
            engine = PersonalityEngine.load_model(str(model_path))
            print(f"已加载预训练模型: {model_path}")
        elif data_path.exists():
            cfg = get_config(n_factors=10)  # 使用完整10因子维度
            engine = PersonalityEngine(cfg)
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            descriptions = [item["description"] for item in data["archetypes"]]
            names = [item["name"] for item in data["archetypes"]]
            parent_ids = [item.get("id", item.get("parent_id", "")) for item in data["archetypes"]]
            engine.train(descriptions, names, parent_ids)
            print(f"已从 full_personas.json 训练引擎（{len(descriptions)}样本）")
        else:
            print("未找到数据文件，启动空引擎")
            engine = PersonalityEngine()
    except Exception as e:
        print(f"API启动初始化失败: {e}")
        engine = PersonalityEngine()


# ═══════════════ 请求模型 ═══════════════

class EmbedRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class MorphRequest(BaseModel):
    seed_index: int = Field(..., ge=0)
    direction_index: int = Field(..., ge=0)
    angle_deg: float = Field(default=30.0, ge=0.0, le=90.0)


class CompareRequest(BaseModel):
    index_a: int = Field(..., ge=0)
    index_b: int = Field(..., ge=0)


class ScoreRequest(BaseModel):
    index_a: int = Field(..., ge=0)
    index_b: int = Field(..., ge=0)


class InteractRequest(BaseModel):
    user_input: str = Field(..., min_length=1, max_length=5000)
    archetype_index: int = Field(default=0, ge=0)
    session_id: Optional[str] = None


class ChatRequest(BaseModel):
    user_input: str = Field(..., min_length=1, max_length=5000)
    archetype_index: int = Field(default=0, ge=0)
    session_id: Optional[str] = None


class MorphTraitsRequest(BaseModel):
    persona_id: str = Field(..., min_length=1)
    adjustments: dict = Field(..., description='{"aggression": +0.2, "warmth": -0.1}')
    new_persona_id: Optional[str] = None


class CloneRequest(BaseModel):
    persona_id: str = Field(..., min_length=1)
    tweaks: dict = Field(default_factory=dict)
    new_persona_id: Optional[str] = None


# ═══════════════ 工具函数 ═══════════════

def get_engine() -> PersonalityEngine:
    if engine is None:
        raise HTTPException(status_code=503, detail="引擎未初始化")
    return engine


def _validate_indices(eng: PersonalityEngine, a: int, b: int, label: str):
    """验证样本索引是否在合法范围内"""
    if eng.factor_scores is None:
        raise HTTPException(status_code=400, detail="引擎未训练，无可用数据")
    max_idx = len(eng.factor_scores) - 1
    for name, idx in [("index_a", a), ("index_b", b)]:
        if idx < 0 or idx > max_idx:
            raise HTTPException(
                status_code=400,
                detail=f"{label}.{name}={idx} 越界，可用范围 0~{max_idx}",
            )


# ═══════════════ API 端点 ═══════════════

@app.get("/")
async def root(_auth: str = Depends(validate_api_key)):
    return {"message": "Personality Core API", "version": "0.1.1"}


@app.post("/embed")
async def embed_text(req: EmbedRequest, _auth: str = Depends(validate_api_key)):
    eng = get_engine()
    return eng.embed(req.text)


@app.get("/factors")
async def list_factors(_auth: str = Depends(validate_api_key)):
    eng = get_engine()
    return eng.ica.get_factor_labels()


@app.get("/clusters")
async def list_clusters(_auth: str = Depends(validate_api_key)):
    eng = get_engine()
    return eng.archetypes


@app.post("/morph")
async def morph_personality(req: MorphRequest, _auth: str = Depends(validate_api_key)):
    eng = get_engine()
    if eng.factor_scores is None:
        raise HTTPException(status_code=400, detail="引擎未训练")
    max_samples = len(eng.factor_scores)
    if req.seed_index >= max_samples:
        raise HTTPException(
            status_code=400,
            detail=f"seed_index={req.seed_index} 越界，范围 0~{max_samples - 1}",
        )
    n_factors = eng.config.n_factors
    if req.direction_index >= n_factors:
        raise HTTPException(
            status_code=400,
            detail=f"direction_index={req.direction_index} 越界，范围 0~{n_factors - 1}",
        )
    return eng.morph(req.seed_index, req.direction_index, req.angle_deg)


@app.post("/score")
async def score_pairing(req: ScoreRequest, _auth: str = Depends(validate_api_key)):
    eng = get_engine()
    _validate_indices(eng, req.index_a, req.index_b, "score")
    return eng.score_pairing(req.index_a, req.index_b)


@app.post("/compare")
async def compare_personalities(req: CompareRequest, _auth: str = Depends(validate_api_key)):
    eng = get_engine()
    _validate_indices(eng, req.index_a, req.index_b, "compare")
    return eng.compare(req.index_a, req.index_b)


@app.get("/atlas")
async def get_atlas(_auth: str = Depends(validate_api_key)):
    eng = get_engine()
    return eng.get_atlas_2d()


@app.post("/interact")
async def interact(req: InteractRequest, _auth: str = Depends(validate_api_key)):
    eng = get_engine()
    # 验证 archetype_index 是否合法
    if req.archetype_index < 0 or req.archetype_index >= len(eng.archetypes):
        raise HTTPException(
            status_code=400,
            detail=f"archetype_index={req.archetype_index} 越界，可用范围 0~{len(eng.archetypes)-1}",
        )
    if eng.emotion_core is None or eng.memory_engine is None:
        eng.initialize_agent(req.archetype_index)
    if req.session_id:
        eng.memory_engine = _get_or_create_session(req.session_id, eng)
    return eng.interact(req.user_input)


@app.post("/chat")
async def chat(req: ChatRequest, _auth: str = Depends(validate_api_key)):
    """LLM 对话接口（需 Ollama 运行中）"""
    eng = get_engine()
    if req.archetype_index < 0 or req.archetype_index >= len(eng.archetypes):
        raise HTTPException(
            status_code=400,
            detail=f"archetype_index={req.archetype_index} 越界，可用范围 0~{len(eng.archetypes)-1}",
        )
    if eng.emotion_core is None or eng.memory_engine is None:
        eng.initialize_agent(req.archetype_index)
    if req.session_id:
        eng.memory_engine = _get_or_create_session(req.session_id, eng)
    response = eng.chat(req.user_input)
    return {
        "response": response,
        "persona_id": eng._resolve_persona_id(),
        "persona_name": eng.current_persona.name if eng.current_persona else "渊",
    }


@app.get("/personas")
async def list_personas(_auth: str = Depends(validate_api_key)):
    """列出所有可用人格档案（包括变体）"""
    eng = get_engine()
    return eng.list_personas()


@app.post("/morph/traits")
async def morph_traits(req: MorphTraitsRequest, _auth: str = Depends(validate_api_key)):
    """在 trait 空间调整人格，生成新变体"""
    eng = get_engine()
    # 先激活该人格
    if eng.current_persona is None or eng.current_persona.persona_id != req.persona_id:
        eng.initialize_by_persona_id(req.persona_id)
    morphed = eng.morph_traits(
        adjustments=req.adjustments,
        new_persona_id=req.new_persona_id,
    )
    return morphed.to_dict()


@app.post("/clone")
async def clone_persona(req: CloneRequest, _auth: str = Depends(validate_api_key)):
    """克隆并微调人格"""
    eng = get_engine()
    if eng.current_persona is None or eng.current_persona.persona_id != req.persona_id:
        eng.initialize_by_persona_id(req.persona_id)
    cloned = eng.morph_traits(
        adjustments=req.tweaks,
        new_persona_id=req.new_persona_id,
    )
    return cloned.to_dict()


@app.post("/train")
async def train_from_descriptions(
    texts: List[str] = Body(..., min_length=1, max_length=200),
    _auth: str = Depends(validate_api_key),
):
    """从文本列表重新训练（仅限本地使用）"""
    global engine
    if engine is None:
        engine = PersonalityEngine()
    # 限制文本长度
    texts = [t[:2000] for t in texts]
    n = len(texts)
    # 自适应参数：样本少时自动减少因子和聚类数
    n_factors = min(5, n - 1, 10)
    n_clusters = min(6, n, 10)
    if n_factors < 2:
        n_factors = 2
    if n_clusters < 2:
        n_clusters = 2

    parent_ids = [f"custom_{i}" for i in range(n)]
    from personality_core.config import get_config as _gc
    engine.config = _gc(n_factors=n_factors, n_clusters=n_clusters)
    engine.train(
        texts,
        [f"样本_{i}" for i in range(n)],
        parent_ids,
    )
    return {"status": "trained", "samples": n, "n_factors": n_factors, "n_clusters": n_clusters}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
