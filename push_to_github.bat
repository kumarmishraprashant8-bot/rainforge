@echo off
echo ===================================================
echo 🐙 Pushing RainForge to GitHub...
echo ===================================================

echo.
echo 1. Initializing Git...
git init

echo.
echo 2. Adding all files...
git add .

echo.
echo 3. Committing changes...
git commit -m "feat: RainForge V1 Release - Final Beast Mode"

echo.
echo 4. Renaming branch to main...
git branch -M main

echo.
echo 5. Adding remote origin...
git remote remove origin 2>nul
git remote add origin https://github.com/kumarmishraprashant8-bot/Rainforge-X.git

echo.
echo 6. Pushing to GitHub...
git push -u origin main

echo.
echo ===================================================
echo ✅ Done! Check your repository now.
echo ===================================================
pause
