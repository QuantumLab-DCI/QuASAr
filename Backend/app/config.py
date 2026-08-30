import os
from pathlib import Path

# --- Project Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_PATH = Path(__file__).resolve().parent
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# --- File Paths ---
SCENARIOS_JSON = os.path.join(DATA_DIR, "scenarios.json")
LOG_FILE = os.path.join(DATA_DIR, "adaptation_changes.log")
MODEL_IMAGE_DIR = os.path.join(DATA_DIR, "feature_model")
STATE_IMAGE_DIR = os.path.join(DATA_DIR, "current_state")

# --- Evidence Files ---
QISKIT_ARTIFACT = "qiskit_circuit_artifact.png"
CIRQ_CIRCUIT_ARTIFACT = "cirq_circuit_artifact.png"
CIRQ_CONVERGENCE_ARTIFACT = "cirq_convergence_artifact.png"

# --- Default Values ---
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 8000
