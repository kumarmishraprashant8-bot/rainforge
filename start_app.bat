@echo off
echo ===================================================
echo 🚀 Launching RainForge Deployment...
echo ===================================================
echo.
echo Phase 1: Building Containers (this may take a few minutes)...
echo.

docker-compose up --build

echo.
echo ===================================================
echo ❌ Server process ended.
echo ===================================================
pause
