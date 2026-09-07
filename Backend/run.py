"""Run the Flask backend from the project directory."""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from app import create_app, setup_startup_tasks
from app.config import DEFAULT_HOST, DEFAULT_PORT

if __name__ == '__main__':
    
    print("Starting the interactive hybrid quantum-classical backend.")
    
    app, feature_model = create_app()

    setup_startup_tasks(feature_model)

    print(f"Server available at http://{DEFAULT_HOST}:{DEFAULT_PORT}.")
    print("Waiting for user interaction.")
    
    use_reloader = os.getenv("FLASK_RELOAD", "").lower() in {"1", "true", "yes"}
    app.run(
        port=DEFAULT_PORT,
        debug=False,
        host=DEFAULT_HOST,
        use_reloader=use_reloader,
    )
