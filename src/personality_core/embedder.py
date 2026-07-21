"""文本嵌入模块 — 将人格描述转化为向量"""
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
import json
import pickle


class TextEmbedder:
    """基于Sentence-BERT的文本嵌入器"""

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_embedding_dimension()

    def encode(self, texts: list[str]) -> np.ndarray:
        """批量编码文本为向量"""
        return self.model.encode(texts, normalize_embeddings=True)

    def encode_single(self, text: str) -> np.ndarray:
        """单条编码"""
        return self.model.encode([text], normalize_embeddings=True)[0]

    def save(self, path: str):
        """保存嵌入模型和维度信息"""
        meta = {"model_name": self.model_name, "dim": self.dim}
        with open(path, "wb") as f:
            pickle.dump(meta, f)
        self.model.save(str(Path(path).parent / "embedder_model"))

    @classmethod
    def load(cls, path: str) -> "TextEmbedder":
        """加载已保存的嵌入器"""
        with open(path, "rb") as f:
            meta = pickle.load(f)
        return cls(model_name=meta["model_name"])
