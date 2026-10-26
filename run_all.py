"""
Campus Connect - Master Launcher
Runs the FastAPI Backend Server in the background and opens the PySimpleGUI Application.
"""

import sys
import threading
import time
import uvicorn
import requests

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import api
import gui_app

def is_api_running() -> bool:
    """Check if API server is already responding."""
    try:
        r = requests.get("http://127.0.0.1:8000/api/health", timeout=1)
        return r.status_code == 200
    except Exception:
        return False

def start_backend():
    """Start uvicorn server in a separate thread if not already running."""
    if is_api_running():
        return
    try:
        config = uvicorn.Config(app=api.app, host="127.0.0.1", port=8000, log_level="warning")
        server = uvicorn.Server(config)
        server.run()
    except Exception as e:
        print(f"Server notice: {e}")

if __name__ == "__main__":
    print("=" * 65)
    print("[*] CAMPUS CONNECT - COLLEGE ISSUE & COMPLAINT SYSTEM")
    print("=" * 65)
    
    if is_api_running():
        print("1. FastAPI Backend is already running on http://127.0.0.1:8000")
        print("   [+] Swagger Docs available at: http://127.0.0.1:8000/docs")
    else:
        print("1. Launching FastAPI Backend Server on http://127.0.0.1:8000 ...")
        server_thread = threading.Thread(target=start_backend, daemon=True)
        server_thread.start()

        # Wait for server readiness
        for _ in range(10):
            if is_api_running():
                print("   [+] FastAPI Backend is Online! (Docs: http://127.0.0.1:8000/docs)")
                break
            time.sleep(0.5)

    print("2. Launching PySimpleGUI Desktop Application ...")
    gui_app.create_gui_app()
    print("Application closed. Goodbye!")
