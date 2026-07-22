# Changelog

## v0.1.4 (2026-07-22)

### 数据
- 新增 `data/full_personas.json`：125 个人格样本（11 基础 + 114 变体）
- 新增 `scripts/generate_synthetic_data.py`：维度扰动法批量生成变体
- 新增 `scripts/enhance_datasets.py`：合并原型+变体，补全对话/morph方向

### 引擎
- `_try_load_external_personas()` 优先加载 `full_personas.json`，回退 `archetypes.json`
- `__init__` 末尾自动调用加载，引擎初始化即含 125 个档案
- `api/server.py` 数据源切换为 `full_personas.json`，n_factors 10

### API
- 新增 `/personas`：列出所有 125 个人格档案
- 新增 `/morph/traits`：在 trait 空间旋转生成变体
- 新增 `/clone`：克隆并微调人格
- 修复 `sys.path` 导入问题

### Web UI
- 重写 `ui/gradio_app.py`：
  - 人格浏览 Tab（下拉选择 → 详情 + 特质条）
  - 人格旋转 Tab（5 维滑块 → 实时生成变体）
  - 图谱 Tab（UMAP/PCA 2D 可视化）
  - 对话 Tab（Chatbot 连接 Ollama）

---

## v0.1.3

- 引擎自动加载 full_personas.json
- API 路径修复

## v0.1.2

- 自动调参 (Optuna)、知识图谱、长时记忆 (FAISS)、工具调度

## v0.1.1

- 16 项 P0/P1 修复（ICA 命名、DEFAULT_CONFIG 污染、GMM 投票等）
- 人格导入导出、trait 预测、Morph→trait 闭环
- CLI (`python -m personality_core`)、Docker 部署

## v0.1.0

- 初始版本：核心引擎（embed → ICA → GMM → morph）
