import re
from .graph_store import G
from sentence_transformers import SentenceTransformer
import numpy as np

# Initialize a simple sentence transformer model for entity embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")

# Cache embeddings for nodes (simple dict)
_emb_cache = {}

def _ensure_embeddings():
    global _emb_cache
    if _emb_cache:
        return
    for node in G.nodes:
        _emb_cache[node] = model.encode(node)

def query(keyword: str, top_k: int = 3) -> str:
    """Return a short textual snippet of the most relevant entities/relations.
    The snippet is a concatenation of "subject - predicate -> object" strings.
    """
    _ensure_embeddings()
    q_vec = model.encode(keyword)
    # Compute cosine similarity
    sims = []
    for node, vec in _emb_cache.items():
        sim = float(np.dot(q_vec, vec) / (np.linalg.norm(q_vec) * np.linalg.norm(vec) + 1e-10))
        sims.append((node, sim))
    sims.sort(key=lambda x: -x[1])
    top_nodes = [n for n, _ in sims[:top_k]]
    snippets = []
    for n in top_nodes:
        # Gather outgoing edges
        for _, rel, obj, attrs in G.out_edges(n, data=True, keys=True):
            snippets.append(f"{n} - {rel} -> {obj}")
    # Return up to top_k snippets
    return "; ".join(snippets[:top_k]) if snippets else ""
