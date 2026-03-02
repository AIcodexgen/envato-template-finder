@echo off
echo 🚀 Envato Template Finder AI - Startup Script
echo ==============================================

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo 📥 Installing dependencies...
pip install -q -r requirements.txt

REM Check for .env file
if not exist ".env" (
    echo ⚠️  Warning: .env file not found!
    echo 📝 Creating .env from .env.example...
    copy .env.example .env
    echo ⚠️  Please edit .env and add your Google API key!
)

echo.
echo ✅ Starting server...
echo 🌐 Open http://localhost:8000 in your browser
echo.

python main.py
pause
