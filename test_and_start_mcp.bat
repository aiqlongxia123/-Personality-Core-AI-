@echo off
cd /d "C:\Users\13534\Desktop\渊"

echo ============================================================
echo   Yuan Personality Core MCP Server - Test Mode
echo ============================================================
echo.

set PERSONALITY_DATA_FILE=C:/Users/13534/Desktop/渊/data/full_personas.json
set PERSONALITY_MODEL_PATH=C:/Users/13534/Desktop/渊/models/personality_model

echo [INFO] Testing MCP Server...
echo.

python tests/test_mcp_tools.py 2>&1

echo.
echo ============================================================
echo   Test Complete!
echo ============================================================
echo.
echo To start the MCP server:
echo   python api/mcp_server.py
echo.
echo Or double-click:
echo   start_mcp.bat
echo.
pause
