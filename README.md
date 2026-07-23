---
title: 渊 — 人格AI系统
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 6.19.0
app_file: app.py
pinned: false
---

# 🧠 Personality Core — 人格AI系统

> 把"性格"变成可计算、可旋转、可克隆的东西。**v0.2.3** | 136 人格档案 | 14 API 端点 | System Prompt 优化 + 场景对话体系 + E2E 增强测试 | pydantic-settings + logging

基于向量嵌入空间的人格分析系统：把人格放进嵌入向量空间，做旋转、聚类、评分、可视化，行为可计算、可克隆。

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| **嵌入** | 文本描述 → 人格向量（Sentence-BERT，默认384维） |
| **因子提取** | FastICA 分解出独立人格维度 |
| **原型聚类** | GMM 将人格分布为不同原型 |
| **人格旋转 (Morph)** | 沿方向轴微调人格，如"更温柔""更锋利" |
| **适配度评分** | 两个人格/场景的匹配度打分 |
| **维度对比** | 多维权度差异分析 |
| **情感引擎** | 情绪动态 + 关系阶段演化 |
| **记忆系统** | 三层记忆 + 成长日志 + 用户兴趣追踪 |
| **LLM对话** | 接入 Ollama 本地模型，按人格风格生成回复 |
| **Prompt 注入防御** | 越狱词检测 + 输入长度截断 + system prompt 片段拦截 |
| **安全策略层** | 自伤 / 医疗 / 隐私 / 侮辱检测，独立于角色设定不可被覆盖 |

## 🎭 预置人格：「渊」

十种女性人格融合为一种完整人格——**渊**。

> 一个从深渊中走出的存在主义者，用手术刀般的理性解剖虚伪，用克制的温度包裹破碎的灵魂。她不拯救你，她让你看见自己。

| 维度 | 分值 |
|------|-----|
| 攻击性 | 0.75 |
| 温暖度 | 0.65 |
| 神秘感 | 0.90 |
| 理性度 | 0.95 |
| 支配性 | 0.80 |

### 灵魂之书

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

> 完整人格档案、拓扑图、三维空间映射、配对矩阵见 [`data/archetypes.md`](data/archetypes.md)；融合人格「渊」的详细定义（行为模式、Prompt 模板、Morph 方向、与 Samantha 对比）见 [`data/fused_archetype.md`](data/fused_archetype.md)。

### 📊 数据集

项目包含 **126 个高质量人格样本**（8 基础 + 118 变体 + 5 新领域人物），覆盖哲学/神学/心理学/文学/即兴/科学/艺术 7 大领域。详见 [`data/full_personas.json`](data/full_personas.json)。配备精细 System Prompt + 5 大场景 × 8 条对话共 40+ 条结构化对话模板，通过 E2E 测试验证。可通过 `scripts/generate_synthetic_data.py` 基于模板批量生成更多变体。

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/aiqlongxia123/-Personality-Core-AI-.git
cd -Personality-Core-AI-

python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e ".[dev]"
```

### 安装为 Hermes 技能（可选）

如果你是 Hermes Agent 用户：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install_hermes_skill.ps1
```

安装后对话自动以「渊」人格回应。说「换清晏」「恢复正常」「换尼采」切换原型。

### 运行 Demo

```bash
python scripts/demo.py
```

### 启动 Web UI

```bash
python ui/gradio_app.py
# 访问 http://localhost:7860
```

### 启动 API 服务

```bash
# 必须先设置 API Key（否则启动失败）
set PERSONALITY_API_KEY=<your-secret-key>    # Windows CMD
$env:PERSONALITY_API_KEY="<your-secret-key>" # PowerShell
export PERSONALITY_API_KEY="<your-secret-key>" # Linux/macOS

python api/server.py
# 访问 http://localhost:8000/docs
```

所有 API 端点均需要 `X-API-Key` 请求头鉴权。完整端点列表：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/embed` | POST | 文本嵌入 |
| `/factors` | GET | 因子标签 |
| `/clusters` | GET | 原型列表 |
| `/morph` | POST | 人格旋转 |
| `/score` | POST | 适配度评分 |
| `/compare` | POST | 维度对比 |
| `/atlas` | GET | 2D 图谱坐标 |
| `/interact` | POST | 无 LLM 交互 |
| `/chat` | POST | LLM 对话 |
| `/personas` | GET | 人格列表 |
| `/morph/traits` | POST | Trait 空间旋转 |
| `/clone` | POST | 克隆微调人格 |
| `/train` | POST | 重新训练引擎 |

### 接入 LLM 对话

需要 [Ollama](https://ollama.com) 运行中：

```bash
ollama serve
```

然后运行 demo，会自动调用本地模型生成人格化回复。

## 🔒 安全说明

- **API 鉴权**：所有端点强制要求 `X-API-Key` 请求头，密钥需 ≥16 位，未配置时服务拒绝启动。
- **Prompt 注入防御**：内置越狱词正则检测 + system prompt 片段拦截 + 输入长度上限（2000字符）。
- **速率限制**：单 IP 每分钟最多 30 次请求，超限返回 429。
- **会话管理**：Session TTL 1小时 + LRU 淘汰（最多50个活跃会话），防止内存泄漏。
- **训练防投毒**：`/train` 端点限制样本数 2~50，文本截断至 2000 字符。
- **安全策略层**：自伤 / 医疗 / 隐私 / 侮辱四类检测独立于角色设定，优先级最高，不可被 Prompt 覆盖。
- **环境变量集中管理**：所有可配置项在 `src/personality_core/settings.py` 统一管理，通过 `.env` 文件覆盖
- **结构化日志**：日志自动输出到控制台 + `./logs/personality_core.log`，便于生产排查
- **依赖锁定**：使用 `pyproject.toml` 锁定全部依赖版本，部署时通过 `pip install -e ".[dev]"` 安装。
- **部署加固**：Docker 容器以非 root 用户运行，`.env` 文件强制 API Key。

## 📐 技术架构

```
文本描述 → Embedding → FastICA(因子) → GMM(原型) → Morph/Scorer/Compare
                                    ↓
                            EmotionCore + MemoryEngine → Agent交互
                                    ↓
                              Ollama LLM → 人格化回复
                                      ↕
                           SafetyPolicy (检测/过滤/拦截)
                              Prompt Injection Filter
```

### Python API

```python
from personality_core.engine import PersonalityEngine
from personality_core.config import DEFAULT_CONFIG

engine = PersonalityEngine(DEFAULT_CONFIG)
engine.train(descriptions, names)

# 嵌入
result = engine.embed("一个冷静但温暖的存在主义者")

# 旋转
morphed = engine.morph(seed_index=0, direction_index=3, angle_deg=45)

# 评分
score = engine.score_pairing(0, 1)

# 对话（需要 Ollama）
engine.initialize_agent(0)
response = engine.chat("你好，我最近很迷茫")
```

## 📁 项目结构

```
personality-core/
├── src/personality_core/    # 核心算法
│   ├── embedder.py          # 文本→向量
│   ├── ica_extractor.py     # ICA因子提取
│   ├── gmm_clusterer.py     # GMM聚类
│   ├── morph.py             # 人格旋转
│   ├── scorer.py            # 适配度评分
│   ├── comparator.py        # 人格对比
│   ├── emotion_core.py      # 情感引擎
│   ├── memory_engine.py     # 三层记忆
│   ├── llm_engine.py        # Ollama对话
│   ├── safety.py            # 安全策略层
│   └── engine.py            # 总控引擎
├── api/                       # FastAPI接口（含Rate Limit、Session管理）
├── ui/                        # Gradio Web UI
├── data/                      # 预置数据集（126个人格样本 + System Prompt + 场景对话）
├── scripts/                   # 训练/演示/审计脚本
├── tests/                     # 单元测试 + 安全专项测试
├── docs/                      # 文档
├── examples/                  # 使用示例
├── pyproject.toml             # 依赖配置
├── Dockerfile                 # 非root容器化部署
├── docker-compose.yml         # 含Ollama服务编排
├── .env.example               # 环境变量模板
├── AUDIT_REPORT.md            # 审计落实报告
├── README.md
├── LICENSE                    # MIT
└── CONTRIBUTING.md
```

## 🔗 相似人格 vs 配对评分

系统可以回答这些问题：

- "清晏和圣母适配吗？" → 0.47 中等适配
- "清晏和弗洛伊德谁更像波伏娃？" → 余弦相似度对比
- "帮我找一个更温柔的清晏" → morph 旋转

## 📚 知识根基

系统的灵魂来自神学/心理学/哲学三大领域的经典著作喂养——详尽清单见 `data/` 目录与 `docs/`。

> 注：书单本身也是人格定义的一部分，公开清单会稀释昭示性，故不在 README 展开。

## ⚙️ 依赖

```
sentence-transformers>=3.0
scikit-learn>=1.4
umap-learn>=0.5
numpy>=1.26
fastapi>=0.110
uvicorn>=0.29
pydantic>=2.0
gradio>=4.0
matplotlib>=3.8
jieba>=0.42
requests>=2.31
```

## 📄 License

MIT License — 自由使用、修改、分发。

## 🤝 Contributing

欢迎提交 PR、Issue、改进文档或补充数据集。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 📝 Changelog

详见 [CHANGELOG.md](CHANGELOG.md)
