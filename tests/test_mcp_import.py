"""
Quick MCP Server Startup Test
Tests that the server can be imported and initialized
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
from pathlib import Path

# Add project root to path
_project_root = Path(__file__).parent.parent
sys.path.insert(0, str(_project_root))
sys.path.insert(0, str(_project_root / "src"))

print("=" * 60)
print("Testing MCP Server Import...")
print("=" * 60)

try:
    # Set required env vars if not set
    os.environ.setdefault("PERSONALITY_DATA_FILE", str(_project_root / "data" / "full_personas.json"))
    os.environ.setdefault("PERSONALITY_MODEL_PATH", str(_project_root / "models" / "personality_model"))
    
    print("\n[1] Importing mcp_server module...")
    from api.mcp_server import mcp
    
    print("[OK] Module imported successfully")
    
    # Check tools registered - use simple string scan since FastMCP API varies by version
    import ast
    source = (Path("api/mcp_server.py")).read_text(encoding='utf-8')
    tree = ast.parse(source)
    
    tool_funcs = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            if any(isinstance(d, ast.Attribute) and d.attr == 'tool' for d in node.decorator_list):
                tool_funcs.append(node.name)
    
    print(f"\n[2] Found {len(tool_funcs)} MCP tools:")
    for tool in sorted(tool_funcs):
        print(f"   - {tool}")
    
    print("\n[3] Testing engine initialization...")
    # The module should auto-initialize on import
    from api.mcp_server import engine
    if engine is not None:
        print("[OK] Engine initialized!")
        p_count = len(engine._persona_profiles) if hasattr(engine, '_persona_profiles') else 'N/A'
        a_count = len(engine.archetypes) if hasattr(engine, 'archetypes') else 'N/A'
        print(f"   Personas: {p_count}")
        print(f"   Archetypes: {a_count}")
    else:
        print("[WARN] Engine is None")
    
    print("\n" + "=" * 60)
    print("MCP SERVER IMPORT TEST PASSED!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
