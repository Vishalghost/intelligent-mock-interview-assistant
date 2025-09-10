@echo off
title Amazon Q CLI Integration Setup
color 0E

echo ========================================
echo   Amazon Q CLI Integration Setup
echo ========================================
echo.

echo [1/3] Installing MCP dependencies...
pip install mcp

echo.
echo [2/3] Setting up Amazon Q configuration...
python amazon_q_integration.py

echo.
echo [3/3] Starting MCP server...
echo.
echo ========================================
echo   Amazon Q CLI Commands Available:
echo.
echo   @interview-assistant start_interview --resume_path "resume.pdf" --role "Software Engineer"
echo   @interview-assistant generate_questions --role "Backend Developer"
echo   @interview-assistant evaluate_answer --question "..." --answer "..." --role "..."
echo   @interview-assistant get_results
echo.
echo   MCP Server is running...
echo ========================================
echo.

python mcp_server.py

pause