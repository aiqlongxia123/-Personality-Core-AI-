"""Personality Core — 基于向量嵌入空间的人格AI系统"""

from .engine import PersonalityEngine, PersonaProfile, BUILTIN_PERSONAS
from .config import get_config, DEFAULT_CONFIG
from .embedder import TextEmbedder
from .ica_extractor import ICAExtractor
from .gmm_clusterer import GMmClusterer
from .morph import morph_vector
from .scorer import PersonalityScorer
from .comparator import PersonalityComparator
from .emotion_core import EmotionCore
from .memory_engine import MemoryAndGrowthEngine
from .llm_engine import LLMChatEngine

from .safety import SafetyPolicy, DEFAULT_SAFETY_POLICY
from .trait_predictor import TraitPredictor

__all__ = [
    "PersonalityEngine",
    "PersonaProfile",
    "BUILTIN_PERSONAS",
    "get_config",
    "DEFAULT_CONFIG",
    "SafetyPolicy",
    "DEFAULT_SAFETY_POLICY",
    "TraitPredictor",
    "TextEmbedder",
    "ICAExtractor",
    "GMmClusterer",
    "morph_vector",
    "PersonalityScorer",
    "PersonalityComparator",
    "EmotionCore",
    "MemoryAndGrowthEngine",
    "LLMChatEngine",
]

__version__ = "0.2.0"
