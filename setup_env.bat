@echo off
echo Setting up environment variables...
echo.
echo Please set your DeepSeek API key:
set /p API_KEY="Enter your DeepSeek API key: "
setx DEEPSEEK_API_KEY "%API_KEY%"
echo.
echo Environment variable set successfully!
echo Please restart your command prompt and run: python run_app_clean.py
pause