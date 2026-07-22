import os
import networkx as nx
from sqlitedict import SqliteDict

# Path to the SQLite DB for the knowledge graph
DB_PATH = os.path.join(os.getenv("APPDATA"), "PersonalityCore", "kg.db")

# Global graph instance (singleton for the process)
G = nx.MultiDiGraph()

def load_db():
    """Load graph nodes/edges from the SQLite store into the in‑memory NetworkX graph."""
    if not os.path.exists(DB_PATH):
        return
    with SqliteDict(DB_PATH, flag='r') as db:
        for key, value in db.items():
            # key is a node identifier, value is a dict of node attributes
            G.add_node(key, **value)
        # edges are stored under a special key "_edges"
        edges = db.get("_edges", [])
        for src, rel, dst, attrs in edges:
            G.add_edge(src, rel, dst, **attrs)

def _save_edges(db, edges):
    db["_edges"] = edges
    db.commit()

def add_triplet(subject: str, predicate: str, obj: str, attrs: dict | None = None):
    """Add a (subject, predicate, object) triple to the graph and persist it.
    ``attrs`` can store extra information about the edge.
    """
    if attrs is None:
        attrs = {}
    G.add_node(subject, type="entity")
    G.add_node(obj, type="entity")
    G.add_edge(subject, predicate, obj, **attrs)
    # Persist the new edge
    with SqliteDict(DB_PATH, autocommit=True) as db:
        # Ensure nodes are saved (overwrite if already exist)
        db[subject] = G.nodes[subject]
        db[obj] = G.nodes[obj]
        # Load existing edges, append the new one, and save back
        edges = db.get("_edges", [])
        edges.append((subject, predicate, obj, attrs))
        _save_edges(db, edges)

# Load persisted graph at import time
load_db()
