import sys
import os

# Ensure Python can find the 'app' modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from app.services.hqc_backends.qiskit_adapter import QiskitAdapter
except ImportError as error:
    print(f"Import error: {error}")
    sys.exit(1)

def test_qiskit_adapter():
    """Run a small Qiskit adapter workload without the MAPE-K controller."""
    print("\nSTARTING DIRECT QISKIT ADAPTER TEST")
    print("===============================================")

    # 1. Instantiate the adapter
    try:
        adapter = QiskitAdapter()
        print("Qiskit adapter instantiated successfully.")
    except Exception as error:
        print(f"Could not instantiate the Qiskit adapter: {error}")
        return

    # 2. Define a compact route-optimization workload for rapid diagnosis.
    parameters = {
        "problem_id": "qiskit_debug_001",
        "problem_complexity": 100,
        "problem_size": 3,
        "circuit_depth": 1,
    }
    algorithm_id = "QAOA"

    print(f"Parameters: {parameters}")
    print(f"Algorithm: {algorithm_id}")
    print("-----------------------------------------------")

    # 3. Execute the job directly
    try:
        result = adapter.execute_job(algorithm_id, parameters)

        print("\nEXECUTION SUCCEEDED")
        print("====================")
        print(f"Objective value: {result.get('objective_value')}")
        print(f"Selected variables: {result.get('selected_variables')}")
        print(f"Artifact URL: {result.get('artifact_url')}")

    except Exception as error:
        print("\nEXECUTION FAILED")
        print("==========================================")
        print(f"Error type: {type(error).__name__}")
        print(f"Message: {error}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_qiskit_adapter()
