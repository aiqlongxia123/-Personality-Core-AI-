"""文本嵌入模块 — 将人格描述转化为向量"""
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
import json
import pickle


class TextEmbedder:
    """基于Sentence-BERT的文本嵌入器"""

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        # 优先用环境变量指定的本地模型路径（ModelScope 等离线环境）
        local_path = os.environ.get("PERSONALITY_MODEL_PATH", "")
        if local_path and Path(local_path).exists():
            model_name = local_path
        self.model_name = model_name
        try:
            # 尝试从本地 HF cache 加载，避免网络请求超时
            cache_path = Path(os.path.expanduser(
                f'~/.cache/huggingface/hub/models--sentence-transformers--{model_name}/snapshots/'
            ))
            if cache_path.exists() and any(p.is_dir() for p in cache_path.iterdir()):
                model_path = list(cache_path.iterdir())[0]
                print(f"[Embedder] Using local HF cache: {model_path}")
                self.model = SentenceTransformer(str(model_path))
                self.dim = self.model.get_embedding_dimension()
                return
        except Exception as e:
            print(f"[Embedder] HF cache not available: {e}")
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
