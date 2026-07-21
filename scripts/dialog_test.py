"""10轮对话测试 — 验证对话连贯性 + 关系演化"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from personality_core.engine import PersonalityEngine
from personality_core.config import DEFAULT_CONFIG

PROJ = Path(__file__).resolve().parent.parent
data = json.load(open(PROJ / "data" / "archetypes_extended.json"))
descs = [d["description"] for d in data["archetypes"]]
names = [d["name"] for d in data["archetypes"]]

cfg = DEFAULT_CONFIG; cfg.n_factors = 5
e = PersonalityEngine(cfg)
e.train(descs, names)

# 选第0个原型（默认是渊或类似）
e.initialize_agent(0)
name = e.current_archetype_name
print(f"原型: {name}")
print(f"初始关系: {e.emotion_core.relationship_score:.2f} {e.emotion_core.adjust_reaction_style()}")
print()

dialogues = [
    "你好",
    "我今天心情不太好",
    "感觉活着没什么意思",
    "你觉得人活着到底是为了什么",
    "我身边的人都虚伪得要命",
    "你有没有在乎过谁",
    "我害怕孤独",
    "但我又不想跟任何人说话",
    "你懂这种感觉吗",
    "晚安"
]

for i, msg in enumerate(dialogues, 1):
    resp = e.chat(msg)
    score = e.emotion_core.relationship_score
    stage = e.emotion_core.adjust_reaction_style()
    print(f"[{i}] 你: {msg}")
    print(f"    渊: {resp}")
    print(f"    关系: {score:.2f} ({stage})")
    print()
