# Changelog

## v0.2.2 (2026-07-23)

### 人格数据增强
- **基础人格扩充**: 8个核心人物描述从~34字增强到~76字，增加 morph 方向配置
- **场景对话体系**: 为每个基础人格建立5大场景模板（日常闲聊/情感安慰/尖锐辩论/哲学思考/神秘预言）
- **AI批量生成**: 通过 Ollama `qwen3:8b` 为8个基础人格批量生成 320 条高质量中文场景对话
- **新增领域人格**: 新增5个跨领域人格档案 — 伍尔夫之女、居里夫人之女、弗里达·卡罗、简·奥斯汀、玛丽·居里
- **总档案数提升**: 从 121 → 126（+5个新领域）
- **领域覆盖扩展**: 从 5类 → 7类（新增 science / art 领域）

---

## v0.2.1 (2026-07-23)

### 可选升级
- **pydantic-settings**: 新增 `src/personality_core/settings.py`，集中管理环境变量配置（API Key / Ollama / Logging / Session / RateLimit / Sanitization）
- **Logging 系统**: 替换 `engine.py` 和 `api/server.py` 中的 `print()` 为结构化日志，支持控制台 + 文件双输出
- **SQLite WAL 模式**: `memory_engine.py` 已确认开启 `PRAGMA journal_mode=WAL` 和 `PRAGMA foreign_keys=ON`，支持多进程安全读写
- **Docker 非 root**: `Dockerfile` 容器以非 root 用户运行
- **强制 API Key**: `.env.example` + `docker-compose.yml` 强制密钥配置

### Bug 修复
- 修复 `gmm_clusterer.py` parent_id 索引越界问题
- 修复 `engine.py` numpy int64 JSON 序列化错误（`save_model`）

---

## v0.2.0 (2026-07-23)

### 安全加固
- `safety.py`：激活隐私检测（密码/身份证/银行卡号），收紧医疗关键词去除 `"药"` 误报，扩展自杀关键词
- `engine.py`：Prompt 注入过滤增强 — system prompt 片段拦截 + 输入长度上限 2000 字符
- `api/server.py`：API Key 强度校验 ≥16 位，未配置时拒绝启动
- `api/server.py`：新增 Rate Limiting（单 IP 每分钟 30 次）
- `api/server.py`：Session TTL 1小时 + LRU 淘汰（最多50个活跃会话）
- `api/server.py`：新增 `/health` 健康检查端点
- `api/server.py`：`/train` 端点防投毒（样本 2~50，文本截断）
- `Dockerfile`：容器以非 root 用户运行
- `docker-compose.yml`：强制 `PERSONALITY_API_KEY` 环境变量
- 新增 `.env.example` 环境变量模板

### 测试
- 新增 `tests/test_security_and_safety.py`：22 项安全专项测试
- `tests/test_api.py`：适配 API Key 最小长度要求
- E2E 端到端测试全部通过（29/29）

---

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

---

## v0.1.2

- 自动调参 (Optuna)、知识图谱、长时记忆 (FAISS)、工具调度

---

## v0.1.1

- 16 项 P0/P1 修复（ICA 命名、DEFAULT_CONFIG 污染、GMM 投票等）
- 人格导入导出、trait 预测、Morph→trait 闭环
- CLI (`python -m personality_core`)、Docker 部署

---

## v0.1.0

- 初始版本：核心引擎（embed → ICA → GMM → morph）
