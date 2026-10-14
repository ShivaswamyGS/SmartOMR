import subprocess
import sys
import os
import time

def main():
    print("==================================================================")
    print("             Starting SmartOMR Full-Stack Application             ")
    print("==================================================================")
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")
    
    # Start Backend
    print("[1/2] Launching FastAPI Backend on http://localhost:8000...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=backend_dir
    )
    
    time.sleep(2)
    
    # Start Frontend
    print("[2/2] Launching Next.js Frontend on http://localhost:3000...")
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        shell=True
    )
    
    print("\nSmartOMR is online!")
    print("  • Web Interface: http://localhost:3000")
    print("  • Backend API Docs: http://localhost:8000/docs")
    print("  • Teacher Login: teacher@smartomr.com / teacher123")
    print("  • Admin Login:   admin@smartomr.com / admin123")
    print("\nPress Ctrl+C to shut down both servers.\n")
    
    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Servers stopped.")

if __name__ == "__main__":
    main()
