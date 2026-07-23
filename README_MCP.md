# 渊 — 本地 MCP Server

基于 [Personality Core](https://github.com/aiqlongxia123/-Personality-Core-AI-) 人格AI系统的本地 MCP (Model Context Protocol) 服务器。

## 功能

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

## 快速开始

### 1. 环境要求

- Python >= 3.10
- pip dependencies: sentence-transformers, scikit-learn, umap-learn, numpy, fastapi, uvicorn, pydantic, jieba

```bash
cd "C:\Users\13534\Desktop\渊"
pip install -r requirements.txt
```

### 2. 配置

复制 `.env.example` 为 `.env`：

```bash
copy .env.example .env
```

编辑 `.env` 设置必要配置。

### 3. 运行 MCP Server

```bash
python api/mcp_server.py
```

Server 启动后会通过 stdio 与 MCP 客户端通信。

### 4. Agnes 配置示例

在 `.agnes/config.yaml` 或项目配置中添加：

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

## 安全特性

- ✅ Prompt注入防护（越狱词检测+长度截断）
- ✅ 安全策略层（自伤/医疗/隐私/侮辱检测）
- ✅ 会话管理（TTL + LRU淘汰）
- ✅ 速率限制（IP级每分钟30请求）
- ✅ 训练防投毒（样本数限制+文本截断）

## 架构

```
MCP Client → stdio → mcp_server.py
                       ↓
              PersonalityEngine
              ├── TextEmbedder (Sentence-BERT)
              ├── ICAExtractor (FastICA)
              ├── GMmClusterer (GMM)
              ├── EmotionCore (情感动态)
              ├── MemoryAndGrowthEngine (三层记忆)
              ├── SafetyPolicy (安全策略)
              └── LLMChatEngine (Ollama/OpenAI)
```

## 人格体系

**11个原型人格** + **融合人格「渊」**

| 人格 | 领域 | 核心特质 |
|------|------|---------|
| 清晏 | 哲学 | 高位审判，病态神性审美 |
| 圣母玛利亚 | 神学 | 无条件爱与牺牲 |
| 弗洛伊德之女 | 心理学 | 拆解欲望，看穿伪装 |
| 波伏娃 | 哲学/女权 | 拒绝被定义 |
| 特蕾莎修女 | 神学 | 苦行奉献 |
| 荣格之女 | 心理学 | 拥抱阴影 |
| 尼采的魔鬼 | 哲学 | 超人意志 |
| 艾丽丝·门罗 | 文学 | 日常中的残酷真相 |
| 奥古斯丁的少女 | 神学 | 罪感与救赎 |
| 阿德勒的女儿 | 心理学 | 自卑→超越 |
| 暴躁娘们 | 即兴 | 嘴硬心软 |
| **渊** | 存在主义 | 从深渊走出的理性者 |

## 依赖

- `sentence-transformers>=3.0`
- `scikit-learn>=1.4`
- `umap-learn>=0.5`
- `numpy>=1.26`
- `fastapi>=0.110`
- `uvicorn[standard]>=0.29`
- `pydantic>=2.0`
- `pydantic-settings>=2.0`
- `jieba>=0.42`
- `mcp>=1.0`

## License

MIT
