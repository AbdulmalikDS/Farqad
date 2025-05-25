import subprocess
import os
import sys
import time
from threading import Thread

def run_frontend_server():
    """Run the front-end FastAPI server"""
    print("Starting front-end server on http://localhost:5001")
    frontend_dir = os.path.join("src", "front-end")
    
    # Use the current Python interpreter to run the script
    python_exe = sys.executable
    
    # Run the server
    process = subprocess.Popen(
        [python_exe, "main.py"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Print output in real-time
    for line in process.stdout:
        print(f"[FRONTEND] {line.strip()}")
    
    process.wait()
    print("Front-end server stopped")

def run_backend_server():
    """Run the main backend FastAPI server"""
    print("Starting main backend server on http://localhost:8000")
    backend_dir = "src"
    
    # Use the current Python interpreter to run the script
    python_exe = sys.executable
    
    # Set up environment with PYTHONPATH including src directory
    env = os.environ.copy()
    src_path = os.path.abspath("src")
    
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = src_path
    
    print(f"Setting PYTHONPATH to include: {src_path}")
    
    # Run the server
    process = subprocess.Popen(
        [python_exe, "main.py"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env
    )
    
    # Print output in real-time
    for line in process.stdout:
        print(f"[BACKEND] {line.strip()}")
    
    process.wait()
    print("Backend server stopped")

if __name__ == "__main__":
    print("Starting both servers...")
    
    # Create threads for each server
    frontend_thread = Thread(target=run_frontend_server)
    backend_thread = Thread(target=run_backend_server)
    
    # Start the servers
    frontend_thread.start()
    time.sleep(1)  # Small delay to avoid mixed output
    backend_thread.start()
    
    try:
        # Keep the main thread alive
        while frontend_thread.is_alive() or backend_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers (this may take a moment)...")
        sys.exit(0) 