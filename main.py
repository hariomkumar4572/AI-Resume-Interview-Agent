import sys
import subprocess
from pathlib import Path


def run():
    """Entry point to launch the Streamlit web application."""
    app_path = Path(__file__).parent / "app.py"
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    subprocess.run(cmd)


if __name__ == "__main__":
    run()
