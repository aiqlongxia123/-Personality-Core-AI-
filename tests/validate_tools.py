"""Final validation - just parse and list tools without loading"""
import ast
from pathlib import Path

source = Path("api/mcp_server.py").read_text(encoding="utf-8")
tree = ast.parse(source)

# Count @mcp.tool decorators by scanning source directly
count = source.count("@mcp.tool()")
print(f"Total @mcp.tool() decorators: {count}")

# Extract function names near decorators
lines = source.split('\n')
tool_funcs = []
for i, line in enumerate(lines):
    if "@mcp.tool()" in line:
        # Next non-empty line should be def func
        for j in range(i+1, min(i+5, len(lines))):
            stripped = lines[j].strip()
            if stripped.startswith("def "):
                tool_funcs.append(stripped.split("(")[0].replace("def ", ""))
                break

print(f"\nExtracted tool functions ({len(tool_funcs)}):")
for f in sorted(tool_funcs):
    print(f"  - {f}")

required = ["chat", "interact", "embed", "morph", "score", "compare", 
            "get_atlas", "list_personas", "list_archetypes", "list_factors",
            "predict_traits", "matrix_compare", "create_custom_persona",
            "morph_traits", "save_model", "train_from_descriptions",
            "get_persona_detail", "health_check"]

missing = [r for r in required if r not in tool_funcs]
if missing:
    print(f"\n[WARNING] Missing: {missing}")
else:
    print(f"\n[SUCCESS] All {len(required)} required tools present!")
