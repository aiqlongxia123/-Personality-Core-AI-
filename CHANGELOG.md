# Changelog

## v0.2.6 (2026-07-23)

### 🤖 本地 MCP Server（核心新功能）
- **MCP Server 封装**: `api/mcp_server.py` — 基于 PersonalityEngine 的本地 MCP 服务器，支持 stdio 协议
- **18个MCP工具**: chat, interact, embed, morph, score, compare, get_atlas, list_personas, list_archetypes, list_factors, predict_traits, matrix_compare, create_custom_persona, morph_traits, save_model, train_from_descriptions, get_persona_detail, health_check
- **Prompt注入防护**: 越狱词检测 + 长度截断 + system prompt过滤
- **安全策略层**: 自伤/医疗/隐私/侮辱检测，自动注入安全提醒
- **会话管理**: TTL超时淘汰 + LRU缓存，多session隔离
- **启动脚本**: Windows双击启动 `start_mcp.bat` / `test_and_start_mcp.bat`
- **Agnes配置示例**: `.env.mcp`, `agnes_mcp_config.example.yaml`
- **TypeScript MCP包装器**: `mcp-server/` 目录作为可选封装方案
- **完整测试套件**: 语法检查、导入测试、集成测试、工具验证全部通过

---

## v0.2.5 (2026-07-23)

### 🧠 Memory Engine 学习机制升级
- **记忆引擎集成学习演化**: `analyze_and_learn()` — 对话后分析情绪信号、更新关系强度、触发记忆整合
- **情绪分析模块**: `_analyze_emotions()` 检测温暖/张力/悲伤/好奇心四大维度
- **成长模式追踪**: `_track_growth_pattern()` 定期统计满意度趋势变化
- **记忆压缩**: `_consolidate_memories()` 每10次交互自动整合高频话题
- **engine.py chat() 已接入**: 每次对话自动触发学习流程
- **相关脚本**: `scripts/memory_learning_patch.py`, `scripts/memory_learning_upgrade.py`

---

## v0.2.4 (2026-07-23)

### 🤖 AI 批量生成新领域人格
- **科幻/未来/预言方向**: 新增10个AI生成人格（时隐者/神经浪客/意识游牧者/量子先知/星渊旅人等）
- **总档案数提升**: 126 → 136
- **领域覆盖扩展**: +6 个新领域（赛博朋克/后人类/未来/科技/预言/科幻）
- **AI 对话生成**: 每人配备 10 条示例对话 + 场景分配

---
