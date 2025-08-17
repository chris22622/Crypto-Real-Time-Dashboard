#!/usr/bin/env python3
"""
Startup script for the Crypto Real-Time Dashboard.
Ensures proper environment and launches Streamlit.
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Launch the crypto dashboard."""
    # Get the project root directory
    project_root = Path(__file__).parent

    # Change to project directory
    os.chdir(project_root)

    # Check if virtual environment exists
    venv_path = project_root / ".venv"
    if not venv_path.exists():
        print("❌ Virtual environment not found. Please run:")
        print("   python -m venv .venv")
        print("   .venv\\Scripts\\activate")
        print("   pip install -r requirements.txt")
        return 1

    # Get the Python executable from venv
    if sys.platform == "win32":
        python_exe = venv_path / "Scripts" / "python.exe"
        streamlit_exe = venv_path / "Scripts" / "streamlit.exe"
    else:
        python_exe = venv_path / "bin" / "python"
        streamlit_exe = venv_path / "bin" / "streamlit"

    if not python_exe.exists():
        print("❌ Python executable not found in virtual environment")
        return 1

    if not streamlit_exe.exists():
        print("❌ Streamlit not found. Installing...")
        subprocess.run([str(python_exe), "-m", "pip", "install", "-r", "requirements.txt"])

    # Launch Streamlit
    print("🚀 Starting Crypto Real-Time Dashboard...")
    print("📊 Dashboard will open in your browser at http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the server")

    try:
        subprocess.run(
            [
                str(streamlit_exe),
                "run",
                "app/main.py",
                "--server.port=8501",
                "--server.headless=false",
            ]
        )
    except KeyboardInterrupt:
        print("\n✅ Dashboard stopped successfully!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
