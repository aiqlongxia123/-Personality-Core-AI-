# 渊 MCP Server 启动指南

## 方法一：直接运行（推荐）

双击 `start_mcp.bat` 即可启动。

## 方法二：命令行启动

```bash
cd "C:\Users\13534\Desktop\渊"

# Windows PowerShell
$env:PERSONALITY_DATA_FILE = "C:/Users/13534/Desktop/渊/data/full_personas.json"
$env:PERSONALITY_MODEL_PATH = "C:/Users/13534/Desktop/渊/models/personality_model"
python api/mcp_server.py

# Linux/macOS
export PERSONALITY_DATA_FILE="/path/to/渊/data/full_personas.json"
export PERSONALITY_MODEL_PATH="/path/to/渊/models/personality_model"
python api/mcp_server.py
```

## Agnes 配置

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

## 验证

启动后，MCP Server 会通过 stdio 与客户端通信。可以使用 MCP Inspector 测试：

```bash
npx @modelcontextprotocol/inspector python api/mcp_server.py
```

## 可用工具

| 工具 | 说明 |
|------|------|
| chat | 与渊人格对话 |
| interact | 无LLM的情感交互 |
| embed | 文本嵌入 |
| morph | 人格旋转 |
| score | 相似度评分 |
| compare | 维度对比 |
| get_atlas | 图谱坐标 |
| list_personas | 人格列表 |
| list_archetypes | 原型聚类 |
| list_factors | ICA因子标签 |
| predict_traits | Trait预测 |
| matrix_compare | 相似度矩阵 |
| create_custom_persona | 创建自定义人格 |
| morph_traits | 调整人格 |
| save_model | 保存模型 |
| train_from_descriptions | 重新训练 |
| get_persona_detail | 人格详情 |
| health_check | 健康检查 |
