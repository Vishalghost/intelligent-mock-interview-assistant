@echo off
title MCP Server - AI Interview Assistant
color 0E

echo ========================================
echo    MCP Server for Amazon Q CLI
echo ========================================
echo.

echo Installing MCP dependencies...
pip install mcp >nul 2>&1

echo.
echo Starting MCP Server...
echo.
echo Available tools:
echo - analyze_resume
echo - generate_questions  
echo - evaluate_answer
echo.
echo Press Ctrl+C to stop the server
echo.

python mcp_server.py

pause