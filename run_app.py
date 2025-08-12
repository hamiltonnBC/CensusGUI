#!/usr/bin/env python3
"""
Simple script to run the CensusConnect application.
"""

import os
import sys
from pathlib import Path

def run_application():
    """Run the Flask application."""
    
    # Change to the backend directory
    backend_dir = Path('codebase/backend')
    
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False
    
    # Check if .env file exists
    env_file = backend_dir / '.env'
    if not env_file.exists():
        print("❌ .env file not found in codebase/backend/")
        print("Please create the .env file with the required configuration.")
        return False
    
    # Change to backend directory and run the app
    os.chdir(backend_dir)
    
    print("🚀 Starting CensusConnect application...")
    print("📍 Backend running at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Run the Flask application
    os.system('python app.py')
    
    return True

if __name__ == "__main__":
    run_application()