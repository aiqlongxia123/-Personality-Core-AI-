# Changelog

## v0.2.3 (2026-07-23)

### 🧠 人格数据增强 (核心)
- **全量合并**: `full_personas.json` 从 121 → 126 档案，包含 5 个新领域人物（伍尔夫之女/居里夫人之女/弗里达·卡罗/简·奥斯汀/玛丽·居里）
- **系统 Prompt 优化**: 为 8 个基础人格生成精细 system prompt（风格/信念/行为准则/示例对话），变体自动继承
- **场景对话体系**: 40 条结构化场景对话（5 场景 × 8 条），覆盖日常闲聊/情感安慰/尖锐辩论/哲学思考/神秘预言
- **E2E 测试新增**: `tests/test_enhanced_data.py` — 验证 126+ 档案完整性、system_prompt、场景对话加载、7 大领域覆盖

### 可选升级
- **pydantic-settings**: 新增 `src/personality_core/settings.py`，集中管理环境变量
- **Logging 系统**: 替换 print() 为结构化日志
- **SQLite WAL 模式**: 多进程安全读写
- **AI 批量生成**: Ollama 生成 320 条对话样本

---

## v0.2.2 (2026-07-23)

### 人格数据增强
- **基础人格扩充**: 8 个核心人物描述从~34字增强到~76字，增加 morph 方向配置
- **场景对话体系**: 为每个基础人格建立 5 大场景模板
- **AI 批量生成**: 通过 Ollama `qwen3:8b` 生成 320 条高质量中文场景对话
- **新增领域人格**: 5 个跨领域人格（文学/科学/艺术）
- **总档案数提升**: 从 121 → 126，领域覆盖 7 类

---

## v0.2.1 (2026-07-23)

### 可选升级
- **pydantic-settings**: `src/personality_core/settings.py` 集中管理环境变量
- **Logging 系统**: 结构化日志，控制台 + 文件双输出
- **SQLite WAL 模式**: 多进程安全读写
- **Docker 非 root**: 容器以非 root 用户运行
- **强制 API Key**: `.env.example` + `docker-compose.yml`

### Bug 修复
- 修复 `gmm_clusterer.py` parent_id 索引越界
- 修复 `engine.py` numpy int64 JSON 序列化

---

## v0.2.0 (2026-07-23)

### 安全加固
- `safety.py`: 隐私检测激活，医疗关键词收紧，自杀关键词扩展
- `engine.py`: Prompt 注入过滤增强
- `api/server.py`: API Key 强度校验 ≥16 位、Rate Limiting、Session TTL/LRU、健康检查、防投毒
- `Dockerfile`: 非 root 运行
- `docker-compose.yml`: 强制 API Key

### 测试
- 22 项安全专项测试全部通过
- E2E 端到端测试 29/29 全部通过

---

## v0.1.4 (2026-07-22)

### 数据
- `data/full_personas.json`：125 个人格样本
- `scripts/generate_synthetic_data.py`：维度扰动法生成变体
- `_try_load_external_personas()` 优先加载 full_personas.json

### API
- `/personas`, `/morph/traits`, `/clone`
- 修复 sys.path 导入问题

### Web UI
- 人格浏览 / 旋转 / 图谱 / 对话 Tab 重写

---

## v0.1.3 ~ v0.1.0
（历史版本记录保持不变）
