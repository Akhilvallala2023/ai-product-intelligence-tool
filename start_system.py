#!/usr/bin/env python3
"""
Quick start script for AI Product Intelligence Tool
Launches both backend and frontend servers
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required")
        return False
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False
    
    # Check if backend dependencies are installed
    try:
        import fastapi
        import openai
        print("✅ Backend dependencies found")
    except ImportError:
        print("❌ Backend dependencies missing")
        print("Please run: pip install -r requirements.txt")
        return False
    
    # Check if frontend dependencies are installed
    frontend_dir = Path("frontend")
    if not (frontend_dir / "node_modules").exists():
        print("❌ Frontend dependencies missing")
        print("Please run: cd frontend && npm install")
        return False
    
    print("✅ All requirements satisfied")
    return True

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting backend server...")
    
    try:
        # Start backend in background
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "backend.main:app", 
            "--reload", "--host", "0.0.0.0", "--port", "8000"
        ])
        
        # Wait a bit for server to start
        time.sleep(3)
        
        # Check if server is running
        import requests
        try:
            response = requests.get("http://localhost:8000/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend server started successfully at http://localhost:8000")
                return backend_process
            else:
                print("❌ Backend server not responding")
                return None
        except:
            print("❌ Backend server failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the React frontend server"""
    print("🚀 Starting frontend server...")
    
    try:
        # Change to frontend directory and start dev server
        frontend_process = subprocess.Popen([
            "npm", "run", "dev"
        ], cwd="frontend")
        
        time.sleep(2)
        print("✅ Frontend server started at http://localhost:5173")
        return frontend_process
        
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def main():
    """Main function to start the system"""
    print("🚀 AI Product Intelligence Tool - Quick Start")
    print("=" * 50)
    
    if not check_requirements():
        print("\n❌ Requirements not met. Please fix the issues above and try again.")
        sys.exit(1)
    
    print("\n🎯 Starting system...")
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend server")
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend server")
        backend_process.terminate()
        sys.exit(1)
    
    print("\n🎉 System started successfully!")
    print("=" * 50)
    print("📱 Frontend: http://localhost:5173")
    print("🔗 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("=" * 50)
    print("\n⚡ Ready to analyze products!")
    print("Press Ctrl+C to stop both servers\n")
    
    try:
        # Wait for user interruption
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print("✅ Servers stopped. Goodbye!")

if __name__ == "__main__":
    main() 