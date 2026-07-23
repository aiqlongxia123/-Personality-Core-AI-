"""
personality_core/system_prompt.py
系统 prompt 管理模块
"""

import json
from pathlib import Path


SYSTEM_PROMPTS = {}
_PROMPT_LOADED = False


def load_system_prompts(data_path: str | None = None):
    """从数据文件加载 system_prompt"""
    global _PROMPT_LOADED, SYSTEM_PROMPTS
    
    if data_path is None:
        data_path = Path(__file__).parent.parent / "data" / "full_personas.json"
    
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for persona in data["archetypes"]:
        pid = persona["id"]
        prompt = persona.get("system_prompt")
        if prompt:
            SYSTEM_PROMPTS[pid] = prompt
    
    _PROMPT_LOADED = True


def get_system_prompt(persona_id: str) -> str | None:
    """获取指定人格的 system prompt"""
    return SYSTEM_PROMPTS.get(persona_id)


def get_all_prompts() -> dict:
    return dict(SYSTEM_PROMPTS)
