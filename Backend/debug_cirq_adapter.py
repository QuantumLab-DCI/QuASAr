"""Run a direct diagnostic workload against the Cirq adapter."""

import sys
import os

# Run directly without installing the project package.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from app.services.hqc_backends.cirq_adapter import CirqAdapter
except ImportError as error:
    print(f"Critical import error: {error}")
    print("Ensure that Cirq and TensorFlow Quantum are installed in the active environment.")
    sys.exit(1)

def test_cirq_adapter():
    """Run a small Cirq adapter workload without the MAPE-K controller."""
    print("\nSTARTING DIRECT CIRQ ADAPTER TEST (TFQ)")
    print("===================================================")

    try:
        adapter = CirqAdapter()
        print("Cirq adapter instantiated successfully.")
    except Exception as error:
        print(f"Could not instantiate the Cirq adapter: {error}")
        return

    # Keep the workload small for quick diagnostics.
    parameters = {
        "problem_id": "cirq_debug_001",
        "problem_complexity": 100,
        "problem_size": 3,
        "circuit_depth": 1,
    }

    algorithm_id = "QAOA"

    print(f"Parameters: {parameters}")
    print(f"Algorithm: {algorithm_id}")
    print("---------------------------------------------------")

    try:
        print("Executing the TensorFlow Quantum simulation...")
        result = adapter.execute_job(algorithm_id, parameters)

        print("\nEXECUTION SUCCEEDED")
        print("====================")
        print(f"Backend: {result.get('backend')}")
        print(f"Objective value: {result.get('objective_value')}")
        print(f"Optimized parameters: {result.get('optimized_parameters')}")

        artifact_url = result.get('artifact_url')
        print(f"Artifact URL: {artifact_url}")

        if artifact_url:
            # Translate the API URL to the artifact's local path.
            artifact_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', os.path.basename(artifact_url)))
            if os.path.exists(artifact_path):
                print(f"Artifact verified on disk: {artifact_path}")
            else:
                print(f"The artifact was not found at the expected path: {artifact_path}")

    except Exception as error:
        print("\nEXECUTION FAILED")
        print("==========================================")
        print(f"Error type: {type(error).__name__}")
        print(f"Message: {error}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cirq_adapter()
