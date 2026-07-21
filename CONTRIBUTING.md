# CONTRIBUTING.md

## 如何贡献

欢迎提交 PR、Issue、改进文档或补充数据集。

### 开发环境

```bash
git clone https://github.com/yourname/personality-core.git
cd personality-core
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

### 代码规范

- Python 3.10+
- 4空格缩进
- f-string 中禁止反斜杠转义
- 未完成逻辑用 `raise NotImplementedError("x")` 占位

### 添加新的人格样本

编辑 `data/archetypes_extended.json`，保持格式一致：

```json
{
  "id": "unique_id",
  "name": "人格名称",
  "description": "人格描述（越详细越好）",
  "source": "original|synthetic",
  "parent_id": "parent_id"
}
```

### 运行测试

```bash
python scripts/demo.py
```

### 提交规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 格式调整
refactor: 重构
test: 测试
chore: 构建/工具
```
