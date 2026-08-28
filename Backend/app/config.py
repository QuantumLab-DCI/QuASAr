import os
from pathlib import Path

# --- Project Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_PATH = Path(__file__).resolve().parent
DATA_DIR = os.path.join(PROJECT_ROOT, 'data') # Fix: data is in Backend/, not Backend/app/

# --- File Paths ---
SCENARIOS_JSON = os.path.join(DATA_DIR, 'scenarios.json')
LOG_FILE = os.path.join(DATA_DIR, 'cambios.log')
MODEL_IMAGE_DIR = os.path.join(DATA_DIR, 'modelo_caracteristicas')
STATE_IMAGE_DIR = os.path.join(DATA_DIR, 'estado_actual')

# --- Evidence Files ---
QISKIT_EVIDENCE = "qiskit_circuit_evidence.png"
CIRQ_CIRCUIT_EVIDENCE = "cirq_circuit_evidence.png"
CIRQ_CONVERGENCE_EVIDENCE = "cirq_convergence_evidence.png"

# --- Default Values ---
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 8000
