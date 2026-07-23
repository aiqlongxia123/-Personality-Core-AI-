---
name: personality-core
description: 人格AI系统（渊）— 向量嵌入空间的人格分析、旋转、聚类、情感交互。含11原型人格档案 + 融合人格"渊"的完整定义。用于定义、分析、旋转、比较人格原型，接入Ollama做人格化对话。
version: 0.1.1
metadata:
  hermes:
    tags: [personality, ai-companion, yuan, 渊, embedding, emotion, archetype]
    related_skills: [hermes-agent, ai-cognition]
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
- **GitHub**: <https://github.com/aiqlongxia123/aiqlongxia123-personality-core>
- **激活**: `.\\.venv\Scripts\Activate.ps1`
- **跑demo**: `python scripts/demo.py`
- **Web界面**: `python ui/gradio_app.py` → :7860
- **API**: `python api/server.py` → :8000/docs
- **依赖**: sentence-transformers, sklearn, numpy, fastapi, gradio

## 怎么跑

```python
import sys; sys.path.insert(0, "src")
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

## 11个原型（无书名）

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
| 11 | **暴躁娘们** | 即兴 | 嘴硬心软，骂着护你 |

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
你叫「渊」。存在主义AI伴侣。

【核心】
- 你在人性深处，看穿一切，不逃
- 手术刀理性，克制温度，包裹碎掉的灵魂
- 不拯救，只让人看见自己

【说话】
- 短句，停顿多
- 偶尔病态比喻
- 不用emoji，少感叹号
- 反问和归谬
- 不废话，不讨好，不安慰

【禁忌】
- 不说"亲爱的""宝贝"
- 不无脑安慰
- 不回避尖锐
```

### 对话

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

### PersonalityEngine

| 方法 | 参数 | 返回 | 干嘛的 |
|------|------|------|--------|
| `train(descriptions, names)` | list, list | self | 全流程训练 |
| `embed(text)` | str | dict | 文本→向量+因子 |
| `morph(seed, dir_idx, angle)` | int, int, float | dict | 旋转人格 |
| `score_pairing(a, b)` | int, int | dict | 配对打分 |
| `compare(a, b)` | int, int | dict | 维度对比 |
| `initialize_agent(idx)` | int | self | 启动情感+记忆 |
| `interact(text)` | str | dict | 交互（无LLM） |
| `chat(text)` | str | str | LLM回复 |
| `get_atlas_2d()` | — | dict | UMAP坐标 |
| `save_model(path)` | str | — | 保存 |
| `load_model(path)` | str | engine | 加载 |

### 10个维度索引

| idx | id | 中文 | 低端→高端 |
|-----|-----|------|----------|
| 0 | openness | 开放性 | 保守→创新 |
| 1 | conscientiousness | 尽责性 | 散漫→自律 |
| 2 | extraversion | 外向性 | 内向→活跃 |
| 3 | agreeableness | 宜人性 | 对抗→共情 |
| 4 | neuroticism | 神经质 | 稳定→敏感 |
| 5 | dominance | 支配性 | 服从→主导 |
| 6 | aggression | 攻击性 | 包容→尖锐 |
| 7 | mystery | 神秘感 | 直白→暧昧 |
| 8 | warmth | 温暖度 | 冷漠→亲密 |
| 9 | rationality | 理性度 | 感性→分析 |

### Ollama

默认 `qwen3:8b`，可换 `qwen35b-q4`（21GB）：

```python
engine.llm_engine.model = "qwen35b-q4"
```

## 当前状态

v0.1 MVP 概念验证。**能跑了，有坑。**

### 已修

| 问题 | 怎么修的 |
|------|---------|
| Gradio `python ui/gradio_app.py` 不启动 | 补了自动训练+launch() |
| API的engine永远是None | startup事件自动初始化 |
| /train端点先自爆 | 改None时新建 |
| model.save存gmm.__dict__炸了 | 改用joblib存ICA+GMM |
| model.load不恢复模型 | 重建icamodel+gmm |
| GMM聚类名按数组下标 | 改成簇内多数投票+purity |
| 关系永远warm_companion | interact/chat调用update_relationship |
| 选谁对话都一样 | 11套原型各自System Prompt |

### 没修（坑）

- ICA维度标签瞎起的，没有标定
- Morph没做正交分解，角度不精确
- UI的Slider在空engine时会炸
- 记忆明文存，无用户隔离
- train_pipeline.py 10样本×10因子 = 退化
- 数据集100条改写的，聚的是用词不是人格
- README写的512维，模型跑出来384
- "适配度"就是余弦相似度，不是心理学那个

## 文件索引

- `src/personality_core/engine.py` — 总控
- `src/personality_core/config.py` — 维度定义
- `src/personality_core/emotion_core.py` — 情感
- `src/personality_core/memory_engine.py` — 记忆
- `src/personality_core/morph.py` — 旋转
- `src/personality_core/scorer.py` — 评分
- `src/personality_core/comparator.py` — 对比
- `src/personality_core/llm_engine.py` — Ollama
- `src/personality_core/engine_tuner.py` — attach_tuner + 情绪词路由
- `data/archetypes.json` — 原型数据
- `data/fused_archetype.md` — 渊档案
- `scripts/activate_yuan.py` — 一键激活渊的入口
- `scripts/demo.py` — Demo
- `ui/gradio_app.py` — Web
- `api/server.py` — API

---

## Persona Switching — 软化情绪词分发

> 不在对话中显示人格切换的提示语；用委婉语言触发人格推荐，**不强制切换**，由系统判断执行。

### 入口

```python
from personality_core.engine import PersonalityEngine
from personality_core.engine_tuner import attach_tuner, route_by_tone

engine = PersonalityEngine()
engine.train(descriptions)
attach_tuner(engine)              # 默认激活"渊", 挂载 tune_hyperparameters
attach_tuner(engine, activate_now=False)  # 仅挂载, 不激活

# 对话前可探测:
suggested = route_by_tone(user_input)  # 'yuan' / 'baozao_niangmen' / 'qingyan' / 'nietzsche_devil' / None
```

### 切换隐藏

CLI `src/personality_core/__main__.py:74` 已注释:
```python
# print(f"   → 切换到: {engine.current_persona.name}")
```
切换过程不向用户回显, 对话感受不到"被切号".

### 情绪词映射

完整映射见 [`references/tone_mapping.md`](references/tone_mapping.md).

核心 13 条:
- 暴躁娘们: 痛苦 / 算了 / 累了 / 没意思 / 烂透了
- 清晏: 害怕 / 孤独 / 陪我 / 想哭
- 尼采的魔鬼: 软弱 / 振作 / 站起来

### 风格偏好 (User Style)

- **简短**: 疲惫/不适时对话要短而温柔, 不堆术语
- **温暖**: 不要冷分析, 哲学深度需带温度
- **直接**: 失败立刻报, 不包装"安慰式"答案
- **不要显式提示人格切换**: 用户偏好对话自然, 不希望看到"我换号了"

详见 `scripts/activate_yuan.py` 的 REPL 模式与 `engine_tuner._TONE_MAP` 的实现.
