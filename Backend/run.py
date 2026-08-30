import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# --- Path Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from app import create_app, setup_startup_tasks
from app.config import DEFAULT_HOST, DEFAULT_PORT

if __name__ == '__main__':
    
    print("Starting the interactive hybrid quantum-classical backend.")
    
    # 1. Create the Flask application instance and obtain the feature model
    app, feature_model = create_app()

    # 2. Run startup tasks (generates the static model image only once)
    setup_startup_tasks(feature_model)

    # 3. Start the Flask server
    print(f"Server available at http://{DEFAULT_HOST}:{DEFAULT_PORT}.")
    print("Waiting for user interaction.")
    
    app.run(port=DEFAULT_PORT, debug=False, host=DEFAULT_HOST)
