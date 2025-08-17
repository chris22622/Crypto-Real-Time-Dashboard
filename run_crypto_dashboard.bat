@echo off
echo 🚀 Starting Crypto Real-Time Dashboard...
echo.

REM Change to the correct directory
cd /d "C:\Users\Chris\Personal Finance Dashboard\crypto-realtime-dashboard"

REM Activate virtual environment and run Streamlit
call "C:\Users\Chris\Personal Finance Dashboard\.venv\Scripts\Activate.bat"
streamlit run app/main.py

echo.
echo Dashboard stopped. Press any key to exit...
pause >nul
