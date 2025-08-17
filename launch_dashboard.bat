@echo off
REM Launch script for crypto dashboard (Windows)

echo 🚀 Starting Crypto Real-Time Dashboard...
echo 📁 Navigating to project directory...

cd /d "c:\Users\Chris\Personal Finance Dashboard\crypto-realtime-dashboard"

echo 🔍 Checking Python environment...
python --version

echo 📦 Checking dependencies...
python -c "import streamlit, pandas, plotly, websocket; print('✅ All dependencies available')" 2>nul
if errorlevel 1 (
    echo ❌ Some dependencies missing. Please run: pip install -r requirements.txt
    pause
    exit /b 1
)

echo 🌐 Starting Streamlit dashboard...
echo 📊 Dashboard will open at: http://localhost:8501
echo.
echo 🛑 Press Ctrl+C to stop the dashboard
echo.

streamlit run app/main.py

pause
