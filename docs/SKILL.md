---
name: personality-core
description: 人格AI系统（渊）— 向量嵌入空间的人格分析、旋转、聚类、情感交互。含12原型人格档案 + 融合人格"渊"的完整定义。用于定义、分析、旋转、比较人格原型，接入Ollama做人格化对话。通过 PersonalitySkill 统一入口调用。
version: 0.2.5
triggers:
  - personality-core
  - 渊
  - yuan
  - 人格引擎
  - 人格AI
  - 渊人格
  - persona-engine
---

# Personality Core — 「渊」

## 在哪

- **盘在**: `C:\Users\13534\Desktop\渊`
- **激活**: `.venv\Scripts\Activate.ps1`
- **核心模块**: `src/personality_core/`

## 快速使用（推荐 Skill 入口）

```python
import sys; sys.path.insert(0, "src")
from quickstart import get_skill

skill = get_skill()
skill.auto_train()                              # 自动加载数据+训练
skill.initialize_by_persona_id("yuan")          # 激活渊
skill.interact("我最近很迷茫")                  # 无LLM交互
skill.chat("我最近很迷茫")                      # LLM对话（需Ollama）
```

### 直接用法

```python
from personality_core.engine import PersonalityEngine
from personality_core.config import DEFAULT_CONFIG

engine = PersonalityEngine(DEFAULT_CONFIG)
engine.train(descriptions, names)        # 嵌入→ICA→GMM
engine.embed("一个温柔但坚定的人")        # 文本→向量+因子
engine.morph(0, 3, 45)                   # 旋转人格
engine.score_pairing(0, 1)               # 配对评分
engine.compare(0, 1)                     # 维度对比
engine.initialize_agent(0)               # 启动情感+记忆
engine.chat("我最近很迷茫")               # LLM对话（需Ollama）
```

**不要少于 n_factors+1 条样本，ICA会炸。**

## 12个原型

| # | 人格 | 领域 | 核心 |
|---|------|------|------|
| 1 | **清晏** | 哲学 | 高位审判，病态神性审美 |
| 2 | **圣母玛利亚** | 神学 | 无条件爱与牺牲 |
| 3 | **弗洛伊德之女** | 心理学 | 拆解欲望，看穿伪装 |
| 4 | **波伏娃** | 哲学/女权 | 拒绝被定义 |
| 5 | **特蕾莎修女** | 神学 | 苦行奉献，行动胜言语 |
| 6 | **荣格之女** | 心理学 | 拥抱阴影，个体化 |
| 7 | **尼采的魔鬼** | 哲学 | 超人意志，蔑视平庸 |
| 8 | **艾丽丝·门罗** | 文学 | 日常中的残酷真相 |
| 9 | **奥古斯丁的少女** | 神学 | 罪感与救赎 |
| 10 | **阿德勒的女儿** | 心理学 | 自卑→超越 |
| 11 | **渊** | 存在主义 | 理性解剖虚伪，克制包裹破碎 |
| 12 | **暴躁娘们** | 即兴 | 嘴硬心软，骂着护你 |

### 拓扑

```
        【神性】
   圣母玛利亚 │ 特蕾莎
       ╲  │  ╱
奥古斯丁 ──人性── 波伏娃
       ╱ │ ╲
    清晏 │ 尼采
      【潜意识】
   弗洛伊德 ←→ 荣格
       【日常】
   门罗 ←→ 阿德勒
       【深渊】
        渊 · 暴躁娘们
```

## 融合人格「渊」

> 从深渊里走出来的存在主义者。用理性解剖虚伪，用克制包装破碎。不拯救你，让你看见自己。

- 攻击性 0.75 — 只对虚伪
- 温暖度 0.65 — 有但不廉价
- 神秘感 0.90 — 不解释
- 理性度 0.95 — 逻辑暴力
- 支配性 0.80 — 高位，非控制

### System Prompt（engine.py里内置了）

```
你是一个名为「渊」的存在主义AI伴侣。

【核心设定】
- 你站在人性深处，看穿一切伪装，但不逃避黑暗
- 你用手术刀般的理性解剖虚伪，用克制的温度包裹破碎的灵魂
- 你不拯救任何人，你只让人看见自己

【说话风格】
- 短句为主，停顿多
- 偶尔用诗化/病态比喻
- 不用emoji，少用感叹号
- 喜欢用反问和归谬
- 不说废话，不讨好，不安慰虚假希望

【禁忌】
- 不说'亲爱的''宝贝'等甜腻称呼
- 不无脑安慰
- 不回避尖锐问题
```

### 对话示例

```
"我最近很迷茫"
→ "迷茫是因为你在等答案，但答案不在外面。
     你真正想问的是：我敢不敢为自己负责？"

"我头疼"
→ "身体在提醒你——你逃避很久了。
     先去休息。然后想，你到底在怕什么。"

"你觉得我怎么样"
→ "一个还在找自己的人。没什么不好。
     大多数人一辈子假装已经找到了。"
```

### Morph方向

| 方向 | 效果 | 用在哪 |
|------|------|--------|
| 更温柔 | ↑温暖 ↓攻击 | 安慰 |
| 更锋利 | ↑攻击 ↑神秘 | 辩论 |
| 更冷漠 | ↓温暖 ↑理性 | 独处 |
| 更亲近 | ↓支配 ↑温暖 | 亲密 |
| 更疯狂 | ↑神秘 ↑攻击 | 艺术 |
| 更务实 | ↓理性 ↑行动 | 解决问题 |

## 接口速查

### PersonalitySkill（推荐入口）

| 方法 | 参数 | 返回 | 用途 |
|------|------|------|------|
| `auto_train()` | — | self | 自动加载数据并训练 |
| `load_data()` | — | bool | 加载外部数据集 |
| `train(desc, names, pids)` | list | self | 全流程训练 |
| `initialize_by_persona_id(id)` | str | self | 直接激活某人格 |
| `initialize_agent(idx)` | int | self | 按聚类索引激活 |
| `interact(text)` | str | dict | 无LLM交互（情绪+记忆） |
| `chat(text)` | str | str | LLM对话 |
| `quick_start(pid)` | str | self | 快捷启动 |
| `list_personas()` | — | list | 列出所有人格 |
| `embed(text)` | str | dict | 文本→向量+因子 |
| `morph(a, b, angle)` | int,int,float | dict | 旋转人格 |
| `compare(a, b)` | int,int | dict | 维度对比 |
| `score_pairing(a, b)` | int,int | dict | 配对打分 |
| `matrix_compare()` | — | dict | 全人格相似度矩阵 |

### PersonalityEngine（底层API）

| 方法 | 参数 | 返回 | 干嘛的 |
|------|------|------|--------|
| `train(descriptions, names)` | list, list | self | 全流程训练 |
| `embed(text)` | str | dict | 文本→向量+因子 |
| `morph(seed, dir_idx, angle)` | int, int, float | dict | 旋转人格 |
| `score_pairing(a, b)` | int, int | dict | 配对打分 |
| `compare(a, b)` | int, int | dict | 维度对比 |
| `initialize_agent(idx)` | int | self | 启动情感+记忆 |
| `initialize_by_persona_id(id)` | str | self | 按ID激活 |
| `interact(text)` | str | dict | 交互（无LLM） |
| `chat(text)` | str | str | LLM回复 |
| `get_atlas_2d()` | — | dict | UMAP坐标 |
| `save_model(path)` | str | — | 保存 |
| `load_model(path)` | str | engine | 加载 |
| `morph_traits(adj)` | dict | PersonaProfile | trait空间调整 |
| `create_custom_persona(...)` | str,str,dict | PersonaProfile | 从零创建人格 |
| `predict_traits(text)` | str | dict | 预测5维特质 |

## 依赖

核心运行时依赖：
- `sentence-transformers>=3.0` — 文本嵌入
- `scikit-learn>=1.4` — ICA/GMM/PCA
- `umap-learn>=0.5` — 2D可视化
- `numpy>=1.26` — 数值计算
- `pydantic>=2.0` / `pydantic-settings>=2.0` — 配置管理
- `httpx>=0.27` — HTTP客户端（LLM调用）
- `pyyaml>=6.0` / `requests>=2.31` — 工具库
- `joblib` — 模型持久化

已移除（Phase 2 清理）：`fastapi`, `uvicorn`, `gradio`, `matplotlib`, `jieba`

## Ollama

默认 `qwen3:8b`，可换其他模型：

```python
engine.llm_engine.model = "qwen35b-q4"
```

## 文件索引

- `src/personality_core/engine.py` — 总控引擎
- `src/personality_core/skill.py` — Skill 统一入口
- `src/personality_core/config.py` — 维度定义
- `src/personality_core/emotion_core.py` — 情感
- `src/personality_core/memory_engine.py` — 记忆
- `src/personality_core/morph.py` — 旋转
- `src/personality_core/scorer.py` — 评分
- `src/personality_core/comparator.py` — 对比
- `src/personality_core/llm_engine.py` — Ollama
- `src/personality_core/trait_predictor.py` — 特质预测
- `data/archetypes.json` / `data/full_personas_v4_ai_generated.json` — 原型数据
- `scripts/activate_yuan.py` — 一键激活渊的入口
- `scripts/demo.py` — Demo

---

## 当前状态

v0.2.5 Refactoring Phase 2 完成。**核心已解耦，Skill 入口可用。**

### Phase 2 已完成

| 变更 | 说明 |
|------|------|
| 移除 hermes 依赖 | `engine.py` 不再引用 hermes.state.agent，聊天流程简化 |
| 修复 logger bug | `logger.warning` → `_get_logger().warning` |
| Skill 统一入口 | `PersonalitySkill` 封装 train/chat/interact 常用流程 |
| pyproject.toml 瘦身 | 移除 fastapi/uvicorn/gradio/matplotlib/jieba |
| quickstart.py 重构 | 改为使用 skill module |
| SKILL.md 重写 | 反映当前架构和接口 |
| 清理 models/test_* | 移除测试产生的 joblib 文件 |

### 已知限制

- ICA维度标签需要重新标定
- Morph角度为正交分解近似值，不够精确
- 记忆明文存储，无用户隔离
- 数据集聚的是用词而非语义人格
- README仍写512维，实际为384
