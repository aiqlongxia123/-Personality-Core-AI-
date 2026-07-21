"""Personality Core — 基于向量嵌入空间的人格AI系统"""

from .engine import PersonalityEngine
from .embedder import TextEmbedder
from .ica_extractor import ICAExtractor
from .gmm_clusterer import GMmClusterer
from .morph import morph_vector
from .scorer import PersonalityScorer
from .comparator import PersonalityComparator

__all__ = [
    "PersonalityEngine",
    "TextEmbedder",
    "ICAExtractor",
    "GMmClusterer",
    "morph_vector",
    "PersonalityScorer",
    "PersonalityComparator",
]

__version__ = "0.1.0"
