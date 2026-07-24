"""Personality Skill - Cross-platform skill wrapper."""
from pathlib import Path
import json
from typing import Optional, List, Dict

from .engine import PersonalityEngine
from .config import get_config, DEFAULT_CONFIG


class PersonalitySkill:
    """Cross-platform personality AI Skill."""
    
    def __init__(self, data_path=None, config=None):
        self.config = config or DEFAULT_CONFIG
        self.engine = PersonalityEngine(self.config)
        self.data_path = Path(data_path) if data_path else Path(__file__).parent.parent / "data"
        self._trained = False
        self._data_loaded = False
        self._loaded_data = []
    
    @property
    def is_trained(self) -> bool:
        return self._trained
    
    def load_data(self) -> bool:
        for name in ["full_personas.json", "full_personas_v4_ai_generated.json", "archetypes.json"]:
            path = self.data_path / name
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if isinstance(data, dict) and "archetypes" in data:
                        self._loaded_data = data["archetypes"]
                    elif isinstance(data, list):
                        self._loaded_data = data
                    self._data_loaded = True
                    return True
                except Exception as e:
                    print(f"Warning: {path}: {e}")
        return False
    
    def train(self, descriptions=None, names=None, parent_ids=None):
        if descriptions is None:
            if not self._data_loaded:
                raise RuntimeError("No data loaded. Call load_data() first.")
            descriptions = [item.get("description","") for item in self._loaded_data if isinstance(item, dict)]
            if not descriptions:
                descriptions = [item.get("name","") for item in self._loaded_data if isinstance(item, dict)]
        if names is None and self._data_loaded:
            names = [item.get("name", f"原型_{i}") for i, item in enumerate(self._loaded_data)]
        if parent_ids is None and self._data_loaded:
            parent_ids = [item.get("id","") or item.get("parent_id","") for item in self._loaded_data]
        self.engine.train(descriptions, names, parent_ids)
        self._trained = True
        return self
    
    def embed(self, text: str) -> dict:
        assert self._trained, "Not trained"
        return self.engine.embed(text)
    
    def morph(self, seed_index: int, direction_index: int, angle_deg: float = 30.0) -> dict:
        assert self._trained, "Not trained"
        return self.engine.morph(seed_index, direction_index, angle_deg)
    
    def score_pairing(self, a: int, b: int) -> dict:
        assert self._trained, "Not trained"
        return self.engine.score_pairing(a, b)
    
    def compare(self, a: int, b: int) -> dict:
        assert self._trained, "Not trained"
        return self.engine.compare(a, b)
    
    def matrix_compare(self) -> dict:
        assert self._trained, "Not trained"
        return self.engine.matrix_compare()
    
    def list_personas(self) -> List[Dict]:
        return self.engine.list_personas()
    
    def initialize_by_persona_id(self, persona_id: str):
        self.engine.initialize_by_persona_id(persona_id)
        return self
    
    def initialize_agent(self, cluster_index: int = 0):
        assert self._trained, "Not trained"
        self.engine.initialize_agent(cluster_index)
        return self
    
    def interact(self, user_input: str) -> dict:
        assert self.engine.emotion_core is not None, "Agent not initialized"
        return self.engine.interact(user_input)
    
    def chat(self, user_input: str) -> str:
        assert self.engine.emotion_core is not None, "Agent not initialized"
        return self.engine.chat(user_input)
    
    def quick_start(self, persona_id: str = "yuan"):
        self.initialize_by_persona_id(persona_id)
        return self
    
    def auto_train(self):
        if self.load_data():
            self.train()
        return self


_skill_instance = None

def get_skill(data_path=None, config=None) -> PersonalitySkill:
    global _skill_instance
    if _skill_instance is None:
        _skill_instance = PersonalitySkill(data_path=data_path, config=config)
    return _skill_instance

def clear_skill():
    global _skill_instance
    _skill_instance = None

__all__ = ["PersonalitySkill", "get_skill", "clear_skill"]
