@echo off
echo 🔥 ULTIMATE FAANG INTERVIEW SYSTEM
echo =======================================
echo.
echo Choose your experience:
echo 1. 💀 PROFESSIONAL INTERVIEW SYSTEM (Extreme Questions) - http://localhost:5002
echo 2. 🏢 Enterprise Web Interface (Advanced) - http://localhost:5001
echo 3. 🎯 Basic Web Interface - http://localhost:5000
echo 4. 💀 Ultimate FAANG CLI (Extreme Difficulty)
echo 5. 📡 MCP Server (Integration)
echo.
set /p choice="Enter choice (1-5): "

if "%choice%"=="1" (
    echo 💀 Starting PROFESSIONAL INTERVIEW SYSTEM on http://localhost:5002
    echo ⚠️  WARNING: EXTREME DIFFICULTY - OUT-OF-THE-BOX THINKING REQUIRED
    echo 💫 Impossible questions, paradox problems, system-breaking challenges
    python professional_app.py
) else if "%choice%"=="2" (
    echo 🚀 Starting Enterprise Web Interface on http://localhost:5001
    python enterprise_app.py
) else if "%choice%"=="3" (
    echo 🌐 Starting Basic Web Interface on http://localhost:5000
    python app.py
) else if "%choice%"=="4" (
    echo 💀 Starting Ultimate FAANG CLI
    echo ⚠️  WARNING: EXTREME DIFFICULTY AHEAD
    python ultimate_faang_system.py
) else if "%choice%"=="5" (
    echo 📡 Starting MCP Server
    python mcp_server.py
) else (
    echo ❌ Invalid choice
    pause
)