"""FastAPI 人格AI系统接口"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import numpy as np
import uvicorn

from personality_core.engine import PersonalityEngine


app = FastAPI(
    title="Personality Core API",
    description="基于向量嵌入空间的人格AI系统",
    version="0.1.0",
)

# 全局引擎实例（由启动事件初始化）
engine: Optional[PersonalityEngine] = None


@app.on_event("startup")
async def startup():
    """启动时自动从数据训练引擎"""
    global engine
    import json
    from pathlib import Path

    data_path = Path(__file__).parent.parent / "data" / "archetypes_extended.json"
    model_path = Path(__file__).parent.parent / "models" / "personality_model.json"

    try:
        if model_path.exists():
            engine = PersonalityEngine.load_model(str(model_path))
            print(f"已加载预训练模型: {model_path}")
        elif data_path.exists():
            from personality_core.config import DEFAULT_CONFIG
            config = DEFAULT_CONFIG
            config.n_factors = 5
            engine = PersonalityEngine(config)
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            descriptions = [item["description"] for item in data["archetypes"]]
            names = [item["name"] for item in data["archetypes"]]
            engine.train(descriptions, names)
            print(f"已从数据训练引擎（{len(descriptions)}样本）")
        else:
            print("未找到数据文件，启动空引擎")
            engine = PersonalityEngine()
    except Exception as e:
        print(f"API启动初始化失败: {e}")
        engine = PersonalityEngine()


class EmbedRequest(BaseModel):
    text: str


class MorphRequest(BaseModel):
    seed_index: int
    direction_index: int
    angle_deg: float = 30.0


class CompareRequest(BaseModel):
    index_a: int
    index_b: int


class ScoreRequest(BaseModel):
    index_a: int
    index_b: int


class InteractRequest(BaseModel):
    user_input: str
    archetype_index: int = 0


def get_engine():
    if engine is None:
        raise RuntimeError("引擎未初始化，请先运行 train_pipeline.py")
    return engine


@app.get("/")
async def root():
    return {"message": "Personality Core API", "version": "0.1.0"}


@app.post("/embed")
async def embed_text(req: EmbedRequest):
    eng = get_engine()
    return eng.embed(req.text)


@app.get("/factors")
async def list_factors():
    eng = get_engine()
    return eng.ica.get_factor_labels()


@app.get("/clusters")
async def list_clusters():
    eng = get_engine()
    return eng.archetypes


@app.post("/morph")
async def morph_personality(req: MorphRequest):
    eng = get_engine()
    return eng.morph(req.seed_index, req.direction_index, req.angle_deg)


@app.get("/score")
async def score_pairing(req: ScoreRequest):
    eng = get_engine()
    return eng.score_pairing(req.index_a, req.index_b)


@app.get("/compare")
async def compare_personalities(req: CompareRequest):
    eng = get_engine()
    return eng.compare(req.index_a, req.index_b)


@app.get("/atlas")
async def get_atlas():
    eng = get_engine()
    return eng.get_atlas_2d()


@app.post("/interact")
async def interact(req: InteractRequest):
    eng = get_engine()
    if eng.emotion_core is None or eng.memory_engine is None:
        eng.initialize_agent(req.archetype_index)
    return eng.interact(req.user_input)


@app.post("/train")
async def train_from_descriptions(req: List[str]):
    global engine
    if engine is None:
        engine = PersonalityEngine()
    engine.train(req)
    return {"status": "trained", "samples": len(req)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
