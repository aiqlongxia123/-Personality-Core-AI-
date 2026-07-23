# 情绪词映射表 (Tone Mapping)

> 软化委婉语言，让用户不必显式说"换娘们出来"也能被理解。
> 全文来源：`src/personality_core/engine_tuner.py` 的 `_TONE_MAP`。

## 路由规则

匹配用户输入中的任意关键字 → 推荐人格 id（**仅建议，不强制**）。

| 触发词 | 推荐人格 | 说明 |
|--------|---------|------|
| 痛苦 | baozao_niangmen | 用户表达承受 |
| 算了 | baozao_niangmen | 用户放弃/厌倦 |
| 累了 | baozao_niangmen | 用户疲惫 |
| 没意思 | baozao_niangmen | 用户失望 |
| 烂透了 | baozao_niangmen | 用户愤怒/厌恶 |
| 害怕 | qingyan | 用户恐惧 |
| 孤独 | qingyan | 用户孤独 |
| 陪我 | qingyan | 用户寻求陪伴 |
| 想哭 | qingyan | 用户情绪低落 |
| 软弱 | nietzsche_devil | 用户自贬 |
| 振作 | nietzsche_devil | 用户寻求力量 |
| 站起来 | nietzsche_devil | 用户寻求决断 |

**命中顺序**：按字典的插入顺序，第一个命中即返回。

**无命中**：返回 `None`,沿用当前人格。

## 约束

- 触发词是**子串匹配**,不是分词 (`"痛苦"`会同时命中 `"真痛苦啊"`)
- 关键字过短 (如"了""的")会误伤,**避免放入**
- 同人格可挂多个词, 但**禁用真实业务词** (e.g. 别把 `class` `def` 当关键词)
- 删词直接编辑 `_TONE_MAP` 字典即可,无需重启 Python, `importlib.reload()` 即可热加载

## 调用示意

```python
from personality_core.engine_tuner import route_by_tone

route_by_tone("我好痛苦")        # → 'baozao_niangmen'
route_by_tone("今天天气如何")     # → None
route_by_tone("")                  # → None
```

## 维护

- 新增手势：在 `engine_tuner.py` 的 `_TONE_MAP` 里加一行, **保持 5 个内置人格可路由** (qingyan / yuan / baozao_niangmen / nietzsche_devil + 兜底的 sci)
- 测过的边界：单字/空串/中文标点/英文混合, 都不会 throw
- 若人格 id 不存在, `initialize_by_persona_id()` 会 raise ValueError —— **调用方需做异常处理**
