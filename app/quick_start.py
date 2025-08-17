#!/usr/bin/env python3
"""
Clean launcher for the Crypto Real-Time Dashboard.
This launcher script provides clean guidance without Streamlit warnings.
"""

def main():
    """Main entry point that provides user guidance."""
    print("🚀 Crypto Real-Time Dashboard")
    print("=" * 50)
    print()
    print("✨ To start the dashboard, run one of these commands:")
    print("   streamlit run app/main.py")
    print("   streamlit run app/launcher.py")
    print()
    print("📂 Or from the app directory:")
    print("   cd app")
    print("   streamlit run main.py")
    print()
    print("⚡ Quick start with batch file:")
    print("   .\\launch_dashboard.bat")
    print()
    print("📊 Dashboard Features:")
    print("  • Real-time cryptocurrency price streaming")
    print("  • Portfolio tracking and management")
    print("  • Technical analysis with indicators")
    print("  • Interactive market heatmap")
    print("  • Price alerts and notifications")
    print("  • News feed and data export")
    print("=" * 50)
    print()
    print("💡 Tip: The dashboard runs on http://localhost:8501 by default")
    print("🚨 Note: Running Python files directly shows warnings. Use streamlit command for best experience.")

if __name__ == "__main__":
    main()
