#!/usr/bin/env python3
"""
Startup script for the IELTS simulation server.
This script starts the FastAPI server with proper configuration.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def start_server():
    """Start the FastAPI server."""
    server_path = Path(__file__).parent / "server.py"

    # if not server_path.exists():
    #     print(f"❌ Server file not found: {server_path}")
    #     return False

    print("🚀 Starting IELTS Test Simulation Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📋 API endpoints:")
    print("   GET  /api/appointments     - Get all appointments")
    print("   POST /api/appointments     - Create new appointment")
    print("   PUT  /api/appointments/{id} - Update appointment")
    print("   DELETE /api/appointments/{id} - Delete appointment")
    print("   DELETE /api/appointments   - Clear all appointments")
    print("   POST /api/reset-test-data  - Reset to sample data")
    print("   GET  /health               - Health check")
    print("   GET  /ielts/timetable      - IELTS timetable page")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)

    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "server:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ], cwd=Path(__file__).parent)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

    return True

if __name__ == "__main__":
    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    print("IELTS Test Simulation Server")
    print("=" * 40)

    if check_requirements():
        start_server()
    else:
        sys.exit(1)
