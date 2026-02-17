import os
import json
from app.config import DATA_DIR, LOG_FILE, SCENARIOS_JSON, QISKIT_EVIDENCE, CIRQ_CIRCUIT_EVIDENCE, CIRQ_CONVERGENCE_EVIDENCE

class FileService:
    @staticmethod
    def read_scenarios():
        try:
            if not os.path.exists(SCENARIOS_JSON):
                return []
            with open(SCENARIOS_JSON, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading scenarios: {e}")
            return []

    @staticmethod
    def read_logs():
        try:
            if not os.path.exists(LOG_FILE):
                return "Waiting for first execution..."
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return "Error reading logs."

    @staticmethod
    def append_log(message: str):
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(message)
        except Exception as e:
            print(f"Error appending log: {e}")

    @staticmethod
    def clear_evidence_files():
        """Elimina imágenes de evidencias antiguas."""
        files_to_remove = [
            QISKIT_EVIDENCE,
            CIRQ_CIRCUIT_EVIDENCE,
            CIRQ_CONVERGENCE_EVIDENCE
        ]
        
        print("🧹 Cleaning old evidence files...")
        for filename in files_to_remove:
            file_path = os.path.join(DATA_DIR, filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"   ⚠️ Could not remove {filename}: {e}")

    @staticmethod
    def get_evidence_path():
        """Returns the path of the existing evidence file, or None."""
        if os.path.exists(os.path.join(DATA_DIR, QISKIT_EVIDENCE)):
            return f"/api/static/{QISKIT_EVIDENCE}"
        if os.path.exists(os.path.join(DATA_DIR, CIRQ_CIRCUIT_EVIDENCE)):
            return f"/api/static/{CIRQ_CIRCUIT_EVIDENCE}"
        if os.path.exists(os.path.join(DATA_DIR, CIRQ_CONVERGENCE_EVIDENCE)):
            return f"/api/static/{CIRQ_CONVERGENCE_EVIDENCE}"
        return None
