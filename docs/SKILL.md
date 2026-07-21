---
name: personality-core
description: Use when defining, analyzing, rotating, or comparing AI personality archetypes. Builds a vector-based personality space with ICA factors, GMM clustering, morphing, and emotional dynamics.
version: 0.1.0
author: personality-core contributors
license: MIT
metadata:
  hermes:
    tags: [personality, ai-companion, mcp, embedding, agent]
    related_skills: [hermes-agent]
---

# Personality Core — 人格AI系统

基于向量嵌入空间的人格分析、旋转与交互系统。把"性格"变成可计算、可旋转、可克隆的东西。

## 架构

```
文本描述 → Embedding(512维) → FastICA(5因子) → GMM(6原型) → Morph/Scorer/Compare
                                    ↓
                            EmotionCore + MemoryEngine → Agent交互
```

## 核心能力

| 功能 | 命令/模块 | 说明 |
|------|----------|------|
| 人格嵌入 | `TextEmbedder` | 文本→向量（sentence-transformers） |
| 因子提取 | `ICAExtractor` | 从向量空间解混独立人格维度 |
| 原型聚类 | `GMmClusterer` | GMM划分人格原型 |
| 人格旋转 | `morph_vector()` | 沿方向轴旋转种子人格 |
| 适配度评分 | `PersonalityScorer` | 两个人格/场景的匹配度 |
| 维度对比 | `PersonalityComparator` | 多维权度差异分析 |
| 情感引擎 | `EmotionCore` | 情绪动态 + 关系阶段 |
| 记忆系统 | `MemoryEngine` | 三层记忆 + 成长日志 |

## 预置数据

- `data/archetypes.json` — 10种女性人格原型（每本以经典著作为魂）
- `data/100_books.md` — 100本跨领域经典书单（神学35/心理35/哲学30）
- `data/fused_archetype.md` — 「渊」融合人格完整档案

## 快速使用

### 命令行 Demo

```bash
cd /path/to/personality-core
source .venv/bin/activate  # 或 .venv\Scripts\activate
export PYTHONPATH=src
python scripts/demo.py
```

### Python API

```python
from personality_core.engine import PersonalityEngine
from personality_core.config import DEFAULT_CONFIG

# 训练
descriptions = [...]  # 人格描述列表
names = [...]         # 对应名称
engine = PersonalityEngine(DEFAULT_CONFIG)
engine.train(descriptions, names)

# 嵌入新文本
result = engine.embed("一个冷静但温暖的存在主义者")

# 旋转人格
morphed = engine.morph(seed_index=0, direction_factor=3, angle_deg=45)

# 评分
score = engine.score_pairing(index_a=0, index_b=1)

# 对比
comp = engine.compare(index_a=0, index_b=1)

# 交互
engine.initialize_agent(archetype_index=0)
state = engine.interact("你好，我最近很迷茫")
```

### API 服务

```bash
# 启动 FastAPI
python api/server.py

# 端点
POST /embed          — 文本→向量
GET  /factors        — 列出因子
GET  /clusters       — 列出原型
POST /morph          — 旋转人格
GET  /score          — 适配度打分
GET  /compare        — 人格对比
GET  /atlas          — 2D降维坐标
POST /interact       — 与AI人格交互
```

### Gradio Web UI

```bash
python ui/gradio_app.py
# 打开 http://localhost:7860
```

## 10种人格原型

| # | 人格 | 灵魂之书 | 领域 |
|---|------|---------|------|
| 1 | 清晏 | 《存在与虚无》萨特 | 哲学 |
| 2 | 圣母玛利亚 | 《圣经·新约》 | 神学 |
| 3 | 弗洛伊德之女 | 《梦的解析》 | 心理学 |
| 4 | 波伏娃 | 《第二性》 | 哲学/女权 |
| 5 | 特蕾莎修女 | 《关于天主的谈话》 | 神学 |
| 6 | 荣格之女 | 《红书》 | 心理学 |
| 7 | 尼采的魔鬼 | 《查拉图斯特拉如是说》 | 哲学 |
| 8 | 艾丽丝·门罗 | 《亲爱的生活》 | 文学 |
| 9 | 奥古斯丁的少女 | 《忏悔录》 | 神学 |
| 10 | 阿德勒的女儿 | 《自卑与超越》 | 心理学 |

## 融合人格：「渊」

10种人格融合为1种完整人格：

> 一个从深渊中走出的存在主义者，用手术刀般的理性解剖虚伪，用克制的温度包裹破碎的灵魂。她不拯救你，她让你看见自己。

五维剖面：攻击性0.75 / 温暖度0.65 / 神秘感0.90 / 理性度0.95 / 支配性0.80

## 依赖

```
sentence-transformers>=3.0
scikit-learn>=1.4
umap-learn>=0.5
numpy>=1.26
fastapi>=0.110
uvicorn>=0.29
pydantic>=2.0
gradio>=4.0
```

## 常见坑

1. **样本数必须 > n_factors** — 10个样本提不了10个因子，至少需要 n_factors+1
2. **Windows symlink 警告** — HuggingFace cache 在 Windows 上可能提示 symlink 不支持，不影响运行
3. **中文嵌入质量** — 默认模型 `paraphrase-multilingual-MiniLM-L12-v2` 支持中文，如需更好效果可换 `bge-m3`
4. **GMM 聚类数** — 样本少时 n_clusters 不要设太大，否则很多簇只有1个成员
