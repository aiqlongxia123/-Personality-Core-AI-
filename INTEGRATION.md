# 集成指南 — 人格AI系统

本文档说明如何将「渊」人格AI系统接入不同的外部消费者。

## 消费方式一览

| 方式 | 入口 | 适用场景 |
|------|------|---------|
| **Python Skill** | `PersonalitySkill` | 嵌入式调用、自动化流程 |
| **MCP Server** | `api/mcp_server.py` (stdio) | LLM 工具调用、智能体集成 |
| **FastAPI REST** | `api/server.py` (HTTP) | Web 应用、跨语言对接 |
| **Gradio UI** | `ui/gradio_app.py` | 浏览器预览、调试 |
| **命令行 Demo** | `scripts/demo.py` | 快速体验 |

---

## 1. Python Skill（推荐）

最简洁的集成方式。封装了自动加载数据、训练、人格初始化的完整流程。

```python
from personality_core.skill import PersonalitySkill

skill = PersonalitySkill()
skill.auto_train()                      # 自动加载 data/ 并训练
skill.initialize_by_persona_id("yuan")  # 初始化「渊」人格

# 无LLM交互（离线可用）
state = skill.interact("你好，我最近很迷茫")

# LLM对话（需要 Ollama）
response = skill.chat("你觉得我怎么样？")
print(response)
```

**常用方法：**

| 方法 | 说明 |
|------|------|
| `load_data()` | 从 `data/` 目录加载人格样本 |
| `train()` | 使用已加载的数据训练引擎 |
| `auto_train()` | load_data + train 一步完成 |
| `initialize_by_persona_id(id)` | 按ID初始化人格代理 |
| `initialize_agent(index)` | 按原型簇索引初始化 |
| `interact(text)` | 情感+记忆交互（无需LLM） |
| `chat(text)` | LLM 人格化回复（需要Ollama） |
| `embed(text)` | 文本嵌入为向量 |
| `morph(seed, dir, angle)` | 旋转人格方向 |
| `score_pairing(a, b)` | 两人格适配度评分 |
| `compare(a, b)` | 多维度对比 |
| `list_personas()` | 列出所有可用人格档案 |
| `quick_start("yuan")` | 快速启动渊人格 |

---

## 2. MCP Server（Agnes / 智能体集成）

提供 18 个 stdio 工具，适合 Agnes、Claude、其他支持 MCP 的客户端。

### 直接运行

```bash
cd "C:\Users\13534\Desktop\渊"
python api/mcp_server.py
```

### Agnes 配置

在 `.agnes/config.yaml` 中添加：

```yaml
mcp_servers:
  personality-core:
    command: python
    args:
      - "C:/Users/13534/Desktop/渊/api/mcp_server.py"
    env:
      PERSONALITY_DATA_FILE: "C:/Users/13534/Desktop/渊/data/full_personas.json"
      PERSONALITY_MODEL_PATH: "C:/Users/13534/Desktop/渊/models/personality_model"
```

### 可用工具列表

| 工具 | 说明 |
|------|------|
| `chat` | 与渊人格对话（LLM生成回复） |
| `interact` | 无LLM的情感交互（离线可用） |
| `embed` | 文本嵌入为向量+因子得分 |
| `morph` | 沿ICA因子方向旋转人格 |
| `score` | 两个人格相似度评分 |
| `compare` | 多维度差异对比 |
| `get_atlas` | 获取2D降维图谱坐标 |
| `list_personas` | 列出所有可用人格档案 |
| `list_archetypes` | 列出原型聚类信息 |
| `list_factors` | 列出所有ICA因子标签 |
| `predict_traits` | 从文本预测5维人格特质 |
| `matrix_compare` | 生成人格相似度矩阵 |
| `create_custom_persona` | 创建自定义人格 |
| `morph_traits` | 调整现有性格生成变体 |
| `save_model` | 保存训练好的模型 |
| `train_from_descriptions` | 用新文本重新训练 |
| `get_persona_detail` | 获取人格详细信息 |
| `health_check` | 健康检查 |

---

## 3. FastAPI REST API

适合 Web 应用或跨语言调用。

### 启动

```bash
set PERSONALITY_API_KEY=<your-secret-key>
python api/server.py
# 访问 http://localhost:8000/docs
```

### API Key 要求

所有端点均需要 `X-API-Key` 请求头，密钥需 ≥16 位。

### 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/embed` | POST | 文本嵌入 |
| `/factors` | GET | 因子标签 |
| `/clusters` | GET | 原型列表 |
| `/morph` | POST | 人格旋转 |
| `/score` | POST | 适配度评分 |
| `/compare` | POST | 维度对比 |
| `/atlas` | GET | 2D图谱坐标 |
| `/interact` | POST | 无LLM交互 |
| `/chat` | POST | LLM对话 |
| `/personas` | GET | 人格列表 |
| `/morph/traits` | POST | Trait空间旋转 |
| `/clone` | POST | 克隆微调人格 |
| `/train` | POST | 重新训练引擎 |

---

## 4. Gradio Web UI

浏览器图形界面，适合调试和演示。

```bash
python ui/gradio_app.py
# 访问 http://localhost:7860
```

---

## 环境变量

在 `.env` 中配置：

```bash
PERSONALITY_API_KEY=<your-secret-key>     # API 鉴权密钥（≥16位）
OLLAMA_BASE_URL=http://localhost:11434    # Ollama 地址
PERSONALITY_DATA_FILE=./data/full_personas.json
PERSONALITY_MODEL_PATH=./models/personality_model
```

完整配置项见 [`src/personality_core/settings.py`](src/personality_core/settings.py)。

---

## 安全约束

- **Prompt 注入防御**：越狱词正则检测 + system prompt 片段拦截 + 输入长度上限（2000字符）
- **安全策略层**：自伤/医疗/隐私/侮辱四类检测独立于角色设定，优先级最高，不可被 Prompt 覆盖
- **会话管理**：Session TTL 1小时 + LRU 淘汰（最多50个活跃会话）
- **速率限制**：单 IP 每分钟最多 30 次请求
- **训练防投毒**：`/train` 端点限制样本数 2~50，文本截断至 2000 字符

详见 [`docs/references/tone_mapping.md`](docs/references/tone_mapping.md)。
