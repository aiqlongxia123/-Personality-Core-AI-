# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.2.5] — 2026-07-24

### Added
- **Skill API (`PersonalitySkill`)** via `src/personality_core/skill.py` and `docs/SKILL.md`
  - Quick-start: `skill.auto_train()` → `skill.initialize_by_persona_id("yuan")`
  - Supports `interact()`, `chat()`, and LLM-powered conversation flows
  - Designed for integration with Agnes/Agentic workflows
- **REFACTORING_REPORT.md** — documents the four-phase Skill refactoring effort

### Changed
- **Phase 1**: Migrated core engine from FastAPI/Gradio-dependent structure to clean dependency model
- **Phase 2**: Extracted PersonalitySkill wrapper exposing unified auto-train + persona-initialization API
- **Phase 3**: Removed MCP Server stdio dependency (`api/mcp_server.py` removed)
- **Phase 4**: Updated documentation, examples, and test suite to align with new Skill-centric workflow

### Removed
- `api/mcp_server.py` — MCP stdio server removed; functionality replaced by Skill API
- Direct FastAPI/Gradio runtime dependency for core functionality (web UI APIs remain optional)

### Fixed
- Cleaned up dependency list in `requirements.txt` and `pyproject.toml`
- Aligned all code references, examples, and docs to v0.2.5 architecture

---
