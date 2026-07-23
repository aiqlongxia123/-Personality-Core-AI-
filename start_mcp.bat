@echo off
cd /d "C:\Users\13534\Desktop\渊"

echo ============================================
echo   渊 Personality Core MCP Server
echo ============================================
echo.

set PERSONALITY_DATA_FILE=C:/Users/13534/Desktop/%~n0/data/full_personas.json
set PERSONALITY_MODEL_PATH=C:/Users/13534/Desktop/%~n0/models/personality_model
set OLLAMA_HOST=http://localhost:11434
set OLLAMA_MODEL=qwen3:8b

echo [INFO] Starting MCP Server...
echo [INFO] Data file: %PERSONALITY_DATA_FILE%
echo [INFO] Model path: %PERSONALITY_MODEL_PATH%
echo.

python api/mcp_server.py

echo.
echo [INFO] Server stopped.
