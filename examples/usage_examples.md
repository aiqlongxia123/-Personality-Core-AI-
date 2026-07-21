# 使用示例

## 基础用法

```python
from personality_core.engine import PersonalityEngine
from personality_core.config import DEFAULT_CONFIG

# 训练
engine = PersonalityEngine(DEFAULT_CONFIG)
descriptions = ["冷静理性的人", "热情温暖的人"]
names = ["理性者", "温暖者"]
engine.train(descriptions, names)

# 嵌入新文本
result = engine.embed("一个温柔但坚定的人")

# 旋转人格
morphed = engine.morph(seed_index=0, direction_factor=3, angle_deg=45)

# 评分
score = engine.score_pairing(0, 1)

# 对比
comp = engine.compare(0, 1)

# 交互
engine.initialize_agent(0)
state = engine.interact("你好")
```

## 命令行 Demo

```bash
cd /path/to/personality-core
source .venv/bin/activate  # Windows: .venv\Scripts\activate
export PYTHONPATH=src      # Windows: $env:PYTHONPATH="src"
python scripts/demo.py
```

## FastAPI 服务

```bash
python api/server.py
# 访问 http://localhost:8000/docs
```

## Gradio Web UI

```bash
python ui/gradio_app.py
# 访问 http://localhost:7860
```

## 与 Ollama 对话

确保 Ollama 运行中：

```bash
ollama serve
```

然后在 Python 中：

```python
engine.initialize_agent(archetype_index=0)
response = engine.chat("你好，我最近很迷茫")
print(response)
```
