@echo off
title Unified AI Interview Assistant
color 0A

echo ========================================
echo   AI Interview Assistant - Unified Setup
echo ========================================
echo.

echo Choose your interface:
echo [1] Web Interface (Browser-based)
echo [2] Amazon Q CLI (Command-line)
echo [3] Both (Dual mode)
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" goto web_only
if "%choice%"=="2" goto cli_only
if "%choice%"=="3" goto both
goto invalid

:web_only
echo.
echo [WEB MODE] Starting Flask web interface...
call setup_and_run.bat
goto end

:cli_only
echo.
echo [CLI MODE] Setting up Amazon Q integration...
call setup_amazon_q.bat
goto end

:both
echo.
echo [DUAL MODE] Setting up both interfaces...
echo.
echo [1/2] Setting up Amazon Q CLI...
python amazon_q_integration.py
echo.
echo [2/2] Starting web interface...
echo.
echo ========================================
echo   Both interfaces available:
echo   - Web: http://localhost:5002
echo   - CLI: Use Amazon Q commands
echo ========================================
echo.
start /b python mcp_server.py
python minimal_app.py
goto end

:invalid
echo Invalid choice. Please run again.
goto end

:end
pause