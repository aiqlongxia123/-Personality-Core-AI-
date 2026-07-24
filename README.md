# 🧠 渊 — 人格AI系统（Abyss Personality AI）

> 把"性格"变成可计算、可旋转、可克隆的东西。**v0.2.5** | MCP Server · Skill · API · CLI · Web UI

基于向量嵌入空间的人格分析系统。将文本描述编码为人格向量，在因子空间中做旋转、聚类、评分与可视化——行为可计算，人格可克隆。

## 架构总览

```
┌─────────────────────────────────────────────────┐
│                 外部消费者                         │
│  Agnes Skill │ MCP Server │ FastAPI │ Gradio UI  │
└──────┬──────────┬──────────┬────────┬────────────┘
       │          │          │        │
       ▼          ▼          ▼        ▼
┌─────────────────────────────────────────────────┐
│           PersonalityEngine（核心引擎）            │
│                                                   │
│  Embedder → ICA → GMM Cluster → Morph / Score     │
│      ↓                                            │
│  EmotionCore + MemoryEngine                        │
│      ↓                                            │
│  LLM Chat (Ollama) + SafetyPolicy                  │
└─────────────────────────────────────────────────┘
```

## 快速使用

### Python API

```python
from personality_core.engine import PersonalityEngine
from personality_core.config import DEFAULT_CONFIG

engine = PersonalityEngine(DEFAULT_CONFIG)
engine.train(descriptions, names)

result = engine.embed("一个冷静但温暖的存在主义者")
morphed = engine.morph(seed_index=0, direction_index=3, angle_deg=45)
score = engine.score_pairing(0, 1)
```

### 作为 Skill 调用

```python
from personality_core.skill import PersonalitySkill

skill = PersonalitySkill()
skill.auto_train()
skill.initialize_by_persona_id("yuan")

state = skill.interact("你好，我最近很迷茫")
response = skill.chat("你觉得我怎么样？")
```

### MCP Server（stdio 模式）

```bash
cd "C:\Users\13534\Desktop\渊"
python api/mcp_server.py
```

提供 18 个工具：`chat`, `interact`, `embed`, `morph`, `score`, `compare`, `list_personas`, `get_atlas`, `matrix_compare`, `create_custom_persona` 等。

### Web UI & API

```bash
python ui/gradio_app.py           # Gradio Web UI → http://localhost:7860
python api/server.py              # FastAPI → http://localhost:8000/docs
```

## 预置人格：「渊」

十种女性人格原型融合为一种完整人格——**渊**。

> 一个从深渊中走出的存在主义者，用手术刀般的理性解剖虚伪，用克制的温度包裹破碎的灵魂。她不拯救你，她让你看见自己。

| 维度 | 分值 |
|------|-----|
| 攻击性 | 0.75 |
| 温暖度 | 0.65 |
| 神秘感 | 0.90 |
| 理性度 | 0.95 |
| 支配性 | 0.80 |

系统包含 **126 个高质量人格样本**，覆盖哲学/神学/心理学/文学/即兴/科学/艺术 7 大领域，详情见 [`data/full_personas.json`](data/full_personas.json)。

## 项目结构

```
渊/
├── src/personality_core/    # 核心算法（引擎、记忆、情感、安全、Trait预测）
│   ├── engine.py            # 总控引擎
│   ├── embedder.py          # 文本→向量嵌入
│   ├── ica_extractor.py     # FastICA 独立因子提取
│   ├── gmm_clusterer.py     # GMM 原型聚类
│   ├── morph.py             # 人格旋转
│   ├── emotion_core.py      # 情感动态引擎
│   ├── memory_engine.py     # 三层记忆系统
│   ├── llm_engine.py        # Ollama 对话引擎
│   ├── safety.py            # 安全策略层
│   └── skill.py             # Skill 封装（自动训练 + 人格初始化）
├── api/
│   ├── server.py            # FastAPI REST 服务
│   └── mcp_server.py        # MCP stdio Server（18 tools）
├── ui/gradio_app.py         # Gradio Web UI
├── data/                    # 预置数据集（126 人格 + System Prompt + 场景对话）
│   ├── archetypes.md        # 10 原行人格档案
│   ├── fused_archetype.md   # 「渊」融合人格完整定义
│   └── full_personas*.json  # 人格向量数据
├── tests/                   # 单元测试 + 安全专项测试
├── docs/SKILL.md            # Skill 使用说明
├── examples/                # Demo 脚本与用法示例
├── scripts/                 # 激活/演示/E2E 测试脚本
├── pyproject.toml           # 依赖配置
└── .env.example             # 环境变量模板
```

## 核心能力

| 能力 | 说明 |
|------|------|
| **文本嵌入** | 文本描述 → Sentence-BERT 人格向量（默认 384 维） |
| **因子分解** | FastICA 分解出独立人格维度 |
| **原型聚类** | GMM 将人格分布为不同原型簇 |
| **人格旋转** | 沿方向轴微调人格（如"更温柔""更锋利"） |
| **适配度评分** | 两个人格的匹配度打分 |
| **多维度对比** | 多维权度差异分析 |
| **情感引擎** | 情绪动态 + 关系阶段演化 |
| **三层记忆** | 工作记忆 / 长期记忆 / 情境感知记忆 |
| **LLM 对话** | 接入 Ollama 本地模型，按人格风格生成回复 |
| **安全策略** | 自伤/医疗/隐私/侮辱检测，优先级最高不可被覆盖 |
| **Prompt 注入防御** | 越狱词检测 + 输入截断 + system prompt 片段拦截 |

## 文档索引

- [`data/archetypes.md`](data/archetypes.md) — 10 种原型人格详细档案
- [`data/fused_archetype.md`](data/fused_archetype.md) — 「渊」融合人格完整定义与行为模式
- [`docs/SKILL.md`](docs/SKILL.md) — Skill 集成说明

## 安装

```bash
pip install -e ".[dev]"
```

需要 Ollama 本地模型支持 LLM 对话功能：

```bash
ollama serve
```

## License

MIT License
