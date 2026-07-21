"""Personality Core — 基于向量嵌入空间的人格AI系统"""

from .engine import PersonalityEngine
from .embedder import TextEmbedder
from .ica_extractor import ICAExtractor
from .gmm_clusterer import GMmClusterer
from .morph import morph_vector
from .scorer import PersonalityScorer
from .comparator import PersonalityComparator
from .emotion_core import EmotionCore
from .memory_engine import MemoryAndGrowthEngine
from .llm_engine import LLMChatEngine

__all__ = [
    "PersonalityEngine",
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

__version__ = "0.1.0"
