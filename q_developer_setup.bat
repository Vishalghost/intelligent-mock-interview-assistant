@echo off
title Q Developer CLI Integration Setup
color 0E

echo ========================================
echo   Q Developer CLI Integration Setup
echo ========================================
echo.

echo [1/3] Installing MCP dependencies...
pip install mcp

echo.
echo [2/3] Setting up Q Developer configuration...
python q_developer_setup.py

echo.
echo [3/3] Starting MCP server...
echo.
echo ========================================
echo   Q Developer CLI Commands Available:
echo.
echo   @interview-assistant analyze_resume --file_path "resume.pdf" --role "Software Engineer"
echo   @interview-assistant generate_questions --role "Frontend Developer" --count 5
echo   @interview-assistant evaluate_answer --question "..." --answer "..." --role "..."
echo   @interview-assistant get_results
echo.
echo   MCP Server is running...
echo   No external AI dependencies required
echo ========================================
echo.

python minimal_mcp_server.py

pause