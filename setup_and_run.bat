@echo off
title AI Interview Assistant Setup
color 0A

echo ========================================
echo    AI-Powered Interview Assistant
echo ========================================
echo.

echo [1/4] Installing dependencies...
pip install flask requests PyPDF2 python-docx cryptography
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Setting up DeepSeek API...
echo.
echo Please enter your DeepSeek API key:
echo (Get it from: https://platform.deepseek.com/)
echo.
set /p API_KEY="API Key: "

if "%API_KEY%"=="" (
    echo WARNING: No API key provided. Using demo mode.
    set API_KEY=demo-key-disabled
)

set DEEPSEEK_API_KEY=%API_KEY%

echo.
echo [3/4] Generating SSL certificates for voice support...
python generate_cert.py >nul 2>&1

echo.
echo [4/4] Starting the application...
echo.
echo ========================================
echo   Application is starting...
echo   
echo   Web Interface: http://localhost:5002
echo   With Voice:    https://localhost:5002
echo   
echo   Press Ctrl+C to stop the server
echo ========================================
echo.

python minimal_app.py

echo.
echo Application stopped. Press any key to exit.
pause >nul