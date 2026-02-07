@echo off
echo ===================================================
echo 🌧️ Starting RainForge Demo Environment...
echo ===================================================

cd backend

if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

echo 🚀 Activating virtual environment...
call venv\Scripts\activate

echo 📥 Checking dependencies...
pip install -r requirements.txt

echo.
echo ===================================================
echo ✅ RainForge Backend is starting!
echo 📝 API Docs: http://localhost:8000/docs
echo ===================================================
echo.

python -m uvicorn app.main_demo:app --reload --port 8000

pause
