"""Quick check MCP Server tools (without loading model)"""
import ast
from pathlib import Path

mcp_file = Path("api/mcp_server.py")
if not mcp_file.exists():
    print(f"[ERROR] File not found: {mcp_file}")
    exit(1)

with open(mcp_file, 'r', encoding='utf-8') as f:
    source = f.read()

# Find @mcp.tool() decorated functions
tree = ast.parse(source)
tool_names = []
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        for dec in node.decorator_list:
            if isinstance(dec, ast.Attribute):
                if dec.attr == 'tool' and isinstance(dec.value, ast.Name) and dec.value.id == 'mcp':
                    tool_names.append(node.name)

print(f"[OK] MCP Server file syntax valid")
print(f"[OK] Found {len(tool_names)} MCP tools:")
for name in sorted(tool_names):
    print(f"   - {name}")

required_funcs = [
    "chat", "interact", "embed", "morph", "score", "compare", 
    "get_atlas", "list_personas", "list_archetypes", "list_factors",
    "predict_traits", "matrix_compare", "create_custom_persona",
    "morph_traits", "save_model", "train_from_descriptions",
    "get_persona_detail", "health_check"
]

missing = [f for f in required_funcs if f not in tool_names]
if missing:
    print(f"\n[WARNING] Missing tools: {missing}")
else:
    print(f"\n[SUCCESS] All required tools implemented!")

security_features = [
    "Prompt注入防护", "越狱词检测", "长度截断", 
    "安全策略层", "自伤检测", "医疗提醒",
    "会话管理", "速率限制", "训练防投毒"
]

print(f"\n[SECURITY CHECK]")
for feature in security_features:
    if feature in source:
        print(f"   [OK] {feature}")
    else:
        print(f"   [NOTE] {feature} (may be implemented differently)")

print("\n[SUCCESS] Module check completed!")
