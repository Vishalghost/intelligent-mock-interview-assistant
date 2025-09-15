@echo off
title Quick Start - AI Voice Interview Assistant
color 0A

echo ========================================
echo   AI VOICE INTERVIEW ASSISTANT
echo ========================================
echo   Secure & AI-Powered Interview Platform
echo ========================================
echo.
echo Features:
echo - Hugging Face AI models for resume analysis
echo - Voice-based interview questions
echo - Real-time speech processing
echo - Multi-dimensional AI evaluation
echo - Comprehensive reporting
echo - Amazon Q CLI integration
echo.
echo Security Features:
echo - CSRF protection enabled
echo - File upload validation
echo - Thread-safe session management
echo - Environment-based configuration
echo.
echo Starting AI Voice Interview System...
echo.
echo [1/3] Installing secure dependencies...
pip install -r requirements.txt
echo.
echo [2/3] Setting up environment...
if not exist .env (
    echo Creating environment file from template...
    copy .env.example .env
    echo Please edit .env file with your configuration before running.
    echo.
)
echo.
echo [3/3] Starting application...
echo Web Interface: http://localhost:5003
echo.
echo IMPORTANT: Make sure to configure .env file with secure values!
echo.
python voice_interview_app.py

pause