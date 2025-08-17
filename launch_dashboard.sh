#!/bin/bash
# Launch script for crypto dashboard

echo "🚀 Starting Crypto Real-Time Dashboard..."
echo "📁 Navigating to project directory..."

cd "c:\Users\Chris\Personal Finance Dashboard\crypto-realtime-dashboard"

echo "🔍 Checking Python environment..."
python --version

echo "📦 Checking dependencies..."
python -c "import streamlit, pandas, plotly, websocket; print('✅ All dependencies available')"

echo "🌐 Starting Streamlit dashboard..."
echo "📊 Dashboard will open at: http://localhost:8501"
echo ""
echo "🛑 Press Ctrl+C to stop the dashboard"
echo ""

streamlit run app/main.py
