# 渊 MCP Server

本地 Personality Core MCP 服务器封装，提供 stdio 协议供 MCP 客户端调用。

## 快速使用

### Agnes 配置

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

### 直接运行

```bash
python api/mcp_server.py
```

## 可用工具 (18个)

| 工具 | 说明 |
|------|------|
| `chat` | 与渊人格对话（LLM生成回复） |
| `interact` | 无LLM的情感交互 |
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

## 安全特性

- ✅ Prompt注入防护
- ✅ 安全策略层（自伤/医疗/隐私/侮辱检测）
- ✅ 会话管理（TTL + LRU淘汰）
- ✅ 速率限制
- ✅ 训练防投毒
