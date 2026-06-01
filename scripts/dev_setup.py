import os
import subprocess

def setup():
    print("Initializing environment...")
    # Setup venv
    subprocess.run(["python", "-m", "venv", "venv"])
    print("Environment ready. Run 'pip install -r requirements.txt' inside venv.")

if __name__ == "__main__":
    setup()
