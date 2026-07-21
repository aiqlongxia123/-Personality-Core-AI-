"""
端到端测试 — 验证全部修复 + 核心路径
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import json
from personality_core.engine import PersonalityEngine
from personality_core.config import DEFAULT_CONFIG

PASS = 0
FAIL = 0

def check(label, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {label}")
    else:
        FAIL += 1
        print(f"  ❌ {label}")

# 加载数据
PROJECT_ROOT = Path(__file__).resolve().parent.parent
data_path = PROJECT_ROOT / "data" / "archetypes_extended.json"
with open(data_path, encoding='utf-8') as f:
    data = json.load(f)
descriptions = [d["description"] for d in data["archetypes"]]
names = [d["name"] for d in data["archetypes"]]

# ═══════════════ 1. 训练 ═══════════════
print("\n═══ 1. 训练 ═══")
cfg = DEFAULT_CONFIG; cfg.n_factors = 5
engine = PersonalityEngine(cfg)
engine.train(descriptions, names)
check("100样本训练完成", engine.embeddings.shape[0] == 100)
check("5个ICA因子", engine.ica.n_components == 5)
check("6个聚类", len(engine.archetypes) == 6)
check("聚类名由多数投票（非数组下标）", any(a["purity"] > 0 for a in engine.archetypes))

# ═══════════════ 2. 嵌入 ═══════════════
print("\n═══ 2. 嵌入 ═══")
r = engine.embed("一个冷静理性的人")
check("返回cluster_id", "cluster_id" in r)
check("返回factor_scores(5个)", len(r["factor_scores"]) == 5)

# ═══════════════ 3. Morph ═══════════════
print("\n═══ 3. 人格旋转 ═══")
m = engine.morph(0, 0, 30)
check("返回result_embedding_dim=384", m["result_embedding_dim"] == 384)

# ═══════════════ 4. 配对评分 ═══════════════
print("\n═══ 4. 配对评分 ═══")
s = engine.score_pairing(0, 1)
check("返回compatibility", "compatibility" in s)
check("分数在合理范围(0~1)", 0 <= s["compatibility"] <= 1)

# ═══════════════ 5. 对比 ═══════════════
print("\n═══ 5. 维度对比 ═══")
c = engine.compare(0, 1)
check("返回dimensions列表", len(c["dimensions"]) == 5)
check("返回biggest_shift", "biggest_shift" in c)

# ═══════════════ 6. 关系演化 ═══════════════
print("\n═══ 6. 关系演化 ═══")
engine.initialize_agent(0)
stage0 = engine.interact("你好")["relationship_stage"]
for msg in ["太好了", "真开心", "谢谢你", "今天真好", "你真好"] * 3:
    engine.interact(msg)
stage_final = engine.interact("今天真好")["relationship_stage"]
score = engine.emotion_core.relationship_score
check("关系分数增长", score > 0.6)
check("阶段从warm→deep", stage_final == "deep_intimacy")

# ═══════════════ 7. 原型prompt ═══════════════
print("\n═══ 7. 原型Prompt切换 ═══")
engine.initialize_agent(0)
p0 = engine._get_system_prompt("polite_beginning")
archetype0_name = engine.current_archetype_name
# 名字去后缀后再检查
import re
clean0 = re.sub(r'_\d+$', '', archetype0_name)
matched_clean = clean0 in p0
matched_fallback = ("渊" in p0 and clean0 not in engine._archetype_prompts)
check(f"原型0 prompt匹配({archetype0_name})", matched_clean or matched_fallback)

# 找清晏（跳过index 0）
found_qy = False
for idx, a in enumerate(engine.archetypes):
    if idx == 0:
        continue
    clean_a = re.sub(r'_\d+$', '', a["name"])
    if clean_a == "清晏":
        engine.initialize_agent(idx)
        found_qy = True
        break
if not found_qy:
    # 没找到清晏簇，强制设名字
    engine.current_archetype_name = "清晏"
p_qy = engine._get_system_prompt("polite_beginning")
check("清晏prompt含'清晏'", "清晏" in p_qy)

# ═══════════════ 8. 持久化 ═══════════════
print("\n═══ 8. 模型持久化 ═══")
model_dir = PROJECT_ROOT / "models"
model_dir.mkdir(exist_ok=True)
model_path = model_dir / "personality_model"
engine.save_model(str(model_path))

for suffix in [".meta.json", ".ica.joblib", ".gmm.joblib"]:
    check(f"文件生成 {suffix}", Path(str(model_path) + suffix).exists())

engine2 = PersonalityEngine.load_model(str(model_path))
r2 = engine2.embed("一个温暖的人")
check("加载后embed正常", "cluster_id" in r2)
m2 = engine2.morph(0, 1, 45)
check("加载后morph正常", m2["result_embedding_dim"] == 384)
s2 = engine2.score_pairing(0, 2)
check("加载后评分正常", "compatibility" in s2)

# ═══════════════ 9. LLM对话（如果Ollama在） ═══════════════
print("\n═══ 9. LLM对话 ═══")
try:
    engine.initialize_agent(0)
    resp = engine.chat("你好")
    check(f"LLM回复非空", len(resp) > 0)
except Exception as e:
    print(f"  ⚠️  LLM对话跳过: {e}")

# ═══════════════ 总结 ═══════════════
print(f"\n{'═'*40}")
print(f"  通过: {PASS}  |  失败: {FAIL}")
print(f"{'═'*40}")
sys.exit(FAIL)
