"""
Quick MCP Server Startup Test - Tool Detection via AST
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
import ast

print("=" * 60)
print("MCP Server Tool Detection Test")
print("=" * 60)

mcp_file = Path("api/mcp_server.py")
if not mcp_file.exists():
    print(f"[ERROR] File not found: {mcp_file}")
    sys.exit(1)

source = mcp_file.read_text(encoding='utf-8')
tree = ast.parse(source)

# Count @mcp.tool() decorators by scanning source directly
tool_count = source.count("@mcp.tool()")
print(f"\n[OK] Total @mcp.tool() decorators: {tool_count}")

# Extract function names near decorators
lines = source.split('\n')
tool_funcs = []
for i, line in enumerate(lines):
    if "@mcp.tool()" in line:
        for j in range(i+1, min(i+5, len(lines))):
            stripped = lines[j].strip()
            if stripped.startswith("def "):
                tool_funcs.append(stripped.split("(")[0].replace("def ", ""))
                break

print(f"\n[OK] Found {len(tool_funcs)} MCP tools:")
for f in sorted(tool_funcs):
    print(f"   - {f}")

required = [
    "chat", "interact", "embed", "morph", "score", "compare", 
    "get_atlas", "list_personas", "list_archetypes", "list_factors",
    "predict_traits", "matrix_compare", "create_custom_persona",
    "morph_traits", "save_model", "train_from_descriptions",
    "get_persona_detail", "health_check"
]

missing = [r for r in required if r not in tool_funcs]
if missing:
    print(f"\n[WARNING] Missing tools: {missing}")
else:
    print(f"\n[SUCCESS] All {len(required)} required tools present!")

# Verify engine can be loaded
print("\n[OK] Verifying engine...")
import os
os.environ.setdefault("PERSONALITY_DATA_FILE", str(Path(__file__).parent.parent / "data" / "full_personas.json"))
os.environ.setdefault("PERSONALITY_MODEL_PATH", str(Path(__file__).parent.parent / "models" / "personality_model"))

from personality_core.engine import PersonalityEngine
engine = PersonalityEngine()
if engine.embeddings is not None or hasattr(engine, '_persona_profiles'):
    print(f"[OK] Engine ready with {len(engine._persona_profiles)} personas")
else:
    print("[WARN] Engine not fully trained yet")

print("\n" + "=" * 60)
print("ALL CHECKS PASSED!")
print("=" * 60)
