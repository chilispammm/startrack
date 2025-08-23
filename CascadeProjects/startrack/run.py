import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def run_server():
    """Run the FastAPI server using uvicorn."""
    print("Starting FastAPI server...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload"],
        cwd=os.getcwd(),
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    return server_process

def install_requirements():
    """Install required Python packages."""
    print("Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def generate_sample_data():
    """Generate sample data if it doesn't exist."""
    data_dir = Path("app/data")
    if not (data_dir / "afcon_players.csv").exists() or not (data_dir / "afcon_events.csv").exists():
        print("Sample data not found. Generating sample data...")
        subprocess.check_call([sys.executable, "scripts/generate_sample_data.py"])
    else:
        print("Sample data already exists. Skipping generation.")

def test_api():
    """Test the API endpoints."""
    print("\nTesting API endpoints...")
    subprocess.check_call([sys.executable, "scripts/test_api.py"])

def main():
    try:
        # Check if requirements are installed
        try:
            import fastapi
            import uvicorn
        except ImportError:
            print("Required packages not found. Installing...")
            install_requirements()
        
        # Generate sample data if needed
        generate_sample_data()
        
        # Start the server
        server_process = run_server()
        
        # Give the server some time to start
        time.sleep(3)
        
        # Open the API docs in the default browser
        webbrowser.open("http://localhost:8000/docs")
        
        print("\nServer is running!")
        print("API Documentation: http://localhost:8000/docs")
        print("Press Ctrl+C to stop the server")
        
        # Wait for the server process to complete
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("\nStopping server...")
            server_process.terminate()
        
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
