#!/usr/bin/env python3
"""
Launcher script for the Crypto Real-Time Dashboard.
This script provides clear guidance for running the dashboard.
"""

def main():
    """Main launcher function."""
    print("🚀 Crypto Real-Time Dashboard")
    print("=" * 50)
    print("This application is designed to run with Streamlit.")
    print()
    print("To start the dashboard, please run one of these commands:")
    print("  streamlit run app/main.py")
    print("  streamlit run app/launcher.py")
    print()
    print("Or from the app directory:")
    print("  cd app")
    print("  streamlit run main.py")
    print("  streamlit run launcher.py")
    print()
    print("📊 Dashboard Features:")
    print("  • Real-time cryptocurrency price streaming")
    print("  • Portfolio tracking and management")
    print("  • Technical analysis with indicators")
    print("  • Interactive market heatmap")
    print("  • Price alerts and notifications")
    print("  • News feed and data export")
    print("  • Multiple themes and customization")
    print("=" * 50)
    print()
    print("💡 Tip: The dashboard runs on http://localhost:8501 by default")

if __name__ == "__main__":
    main()
