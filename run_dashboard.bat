@echo off
cd /d "C:\Users\Chris\Personal Finance Dashboard\crypto-realtime-dashboard"
call .venv\Scripts\activate.bat
streamlit run app\main.py
