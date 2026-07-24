"""
Personality Core — 快速入口（Skill 模式）

用法:
    from quickstart import *
    skill = get_skill()
    skill.auto_train()                 # 自动加载数据+训练
    skill.chat("你好")                 # LLM对话（需Ollama）
    skill.initialize_by_persona_id("yuan")
    skill.interact("我最近很迷茫")     # 无LLM交互
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from personality_core.skill import PersonalitySkill, get_skill, clear_skill
from personality_core.engine import PersonalityEngine
from personality_core.config import DEFAULT_CONFIG

__all__ = [
    "PersonalitySkill",
    "get_skill",
    "clear_skill",
    "PersonalityEngine",
    "DEFAULT_CONFIG",
    "PROJECT_ROOT",
    "SRC_PATH",
]
