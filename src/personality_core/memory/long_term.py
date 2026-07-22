import os, json, numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Try to import FAISS; if not available we fall back to a simple NumPy list implementation
try:
    import faiss
except Exception:
    faiss = None

# Directory for persistent data
BASE_DIR = Path(os.getenv('APPDATA')) / 'PersonalityCore'
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Paths for index and metadata
INDEX_PATH = BASE_DIR / 'lt_index.faiss'
META_PATH = BASE_DIR / 'lt_meta.json'

# Embedding model (shared across calls)
_model = SentenceTransformer('all-MiniLM-L6-v2')

# Internal state (initialized lazily)
_index = None          # FAISS index when available
_vectors = []          # fallback list of vectors (numpy arrays)
_ids = []              # IDs corresponding to _vectors
_meta = {}

def _init_index():
    """Load existing FAISS index or create a new one.
    If FAISS is unavailable, keep using the pure‑Python fallback.
    """
    global _index
    if faiss is None:
        return
    if INDEX_PATH.exists():
        _index = faiss.read_index(str(INDEX_PATH))
    else:
        # 384 is the dimension of the sentence‑transformer model used above
        _index = faiss.IndexFlatL2(384)

def _load_meta():
    """Load metadata and, if needed, fallback vectors/IDs from disk."""
    global _meta, _vectors, _ids
    if META_PATH.exists():
        with open(META_PATH, 'r', encoding='utf-8') as f:
            _meta = json.load(f)
        # Re‑create fallback vectors if FAISS is not available
        if faiss is None:
            vec_path = BASE_DIR / 'lt_vectors.npy'
            id_path = BASE_DIR / 'lt_ids.npy'
            if vec_path.exists() and id_path.exists():
                _vectors = [v for v in np.load(vec_path, allow_pickle=True)]
                _ids = list(np.load(id_path, allow_pickle=True).astype(int))
    else:
        _meta = {}

def _save():
    """Persist the FAISS index (if any) and meta JSON.
    In fallback mode we also persist vectors & ids as .npy files.
    """
    if faiss is not None and _index is not None:
        faiss.write_index(_index, str(INDEX_PATH))
    with open(META_PATH, 'w', encoding='utf-8') as f:
        json.dump(_meta, f, ensure_ascii=False, indent=2)
    if faiss is None:
        # Save fallback vectors
        vec_path = BASE_DIR / 'lt_vectors.npy'
        id_path = BASE_DIR / 'lt_ids.npy'
        if _vectors:
            np.save(vec_path, np.stack(_vectors))
        else:
            np.save(vec_path, np.empty((0, 384)))
        np.save(id_path, np.array(_ids, dtype=int))

# Initialize on module import
_init_index()
_load_meta()

def add(text: str):
    """Add a text snippet to the long‑term memory store.
    The snippet is embedded, stored in the index (or fallback list), and meta is persisted.
    """
    global _index, _vectors, _ids, _meta
    vec = _model.encode(text)
    idx = len(_meta)
    if faiss is not None and _index is not None:
        _index.add(np.expand_dims(vec, 0))
    else:
        _vectors.append(vec)
        _ids.append(idx)
    _meta[idx] = {'text': text}
    _save()

def search(query: str, k: int = 5):
    """Return up to *k* most similar stored texts.
    Uses cosine similarity (FAISS L2 index works as a proxy for cosine after normalisation).
    """
    if not _meta:
        return []
    q_vec = _model.encode(query)
    if faiss is not None and _index is not None:
        D, I = _index.search(np.expand_dims(q_vec, 0), k)
        results = []
        for i in I[0]:
            i_int = int(i)
            if i_int in _meta:
                results.append(_meta[i_int]['text'])
        return results
    else:
        # Compute cosine similarity manually over fallback vectors
        sims = []
        for idx, vec in zip(_ids, _vectors):
            sim = float(np.dot(q_vec, vec) / (np.linalg.norm(q_vec) * np.linalg.norm(vec) + 1e-10))
            sims.append((idx, sim))
        sims.sort(key=lambda x: -x[1])
            # 兼容 np.int64 键以及可能的 string 键
    results = []
    for idx, _ in sims[:k]:
        i_int = int(idx)
        if i_int in _meta:
            results.append(_meta[i_int]['text'])
        elif str(i_int) in _meta:
            results.append(_meta[str(i_int)]['text'])
    return results
