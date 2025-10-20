#!/usr/bin/env python3
"""
Backend Development Server Launcher
Easy startup script for CrewAI Studio API
"""
import subprocess
import sys
import os
from pathlib import Path


def main():
    """Launch the FastAPI development server"""

    print("🚀 Starting CrewAI Studio Backend API...")
    print()

    # Check if we're in the correct directory
    if not Path("main.py").exists():
        print("❌ Error: main.py not found!")
        print("   Please run this script from the bend/ directory")
        sys.exit(1)

    # Check if virtual environment should be used
    venv_path = Path("venv")
    if venv_path.exists():
        print("🔧 Using virtual environment...")
        if sys.platform == "win32":
            python_cmd = str(venv_path / "Scripts" / "python.exe")
        else:
            python_cmd = str(venv_path / "bin" / "python")
    else:
        print("ℹ️  No virtual environment found, using system Python")
        python_cmd = sys.executable

    # Install dependencies
    print("📥 Checking dependencies...")
    try:
        subprocess.run(
            [python_cmd, "-m", "pip", "install", "-q", "-r", "requirements.txt"],
            check=True
        )
    except subprocess.CalledProcessError:
        print("⚠️  Warning: Failed to install some dependencies")

    # Display server info
    print()
    print("✨ Starting FastAPI server...")
    print("📍 API Documentation: http://localhost:8000/docs")
    print("📍 Health Check: http://localhost:8000/api/health")
    print("📍 Root: http://localhost:8000/")
    print()
    print("Press CTRL+C to stop the server")
    print("-" * 50)
    print()

    # Run the server
    try:
        subprocess.run([python_cmd, "main.py"], check=True)
    except KeyboardInterrupt:
        print()
        print("👋 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
