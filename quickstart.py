"""
Personality Core — 快速入口

用法:
    from quickstart import *
    engine = PersonalityEngine(DEFAULT_CONFIG)
    engine.train(descriptions, names)
    engine.chat("你好")
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from personality_core.engine import PersonalityEngine
from personality_core.config import DEFAULT_CONFIG, DIMENSIONS, DIMENSION_INDEX
from personality_core.morph import morph_vector, morph_factor_score
from personality_core.scorer import PersonalityScorer
from personality_core.comparator import PersonalityComparator
from personality_core.emotion_core import EmotionCore
from personality_core.llm_engine import LLMChatEngine

__all__ = [
    "PersonalityEngine",
    "DEFAULT_CONFIG",
    "DIMENSIONS",
    "DIMENSION_INDEX",
    "morph_vector",
    "morph_factor_score",
    "PersonalityScorer",
    "PersonalityComparator",
    "EmotionCore",
    "LLMChatEngine",
    "PROJECT_ROOT",
    "SRC_PATH",
]
