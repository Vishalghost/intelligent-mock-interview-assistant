@echo off
echo Setting up GitHub repository...
echo.

REM Initialize git repository
git init

REM Add all files
git add .

REM Initial commit
git commit -m "Initial commit: Professional Interview Assessment Platform with AI integration"

echo.
echo Repository initialized!
echo.
echo Next steps:
echo 1. Create a new repository on GitHub.com
echo 2. Copy the repository URL
echo 3. Run: git remote add origin YOUR_GITHUB_URL
echo 4. Run: git push -u origin main
echo.
pause