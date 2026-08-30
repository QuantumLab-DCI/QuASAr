import sys
import os

# 1. Configure the path to find the 'app' modules
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

    # 2. Instantiate the adapter
    try:
        adapter = CirqAdapter()
        print("Cirq adapter instantiated successfully.")
    except Exception as error:
        print(f"Could not instantiate the Cirq adapter: {error}")
        return

    # 3. Define test parameters
    # Use 3 nodes and depth 1 for a quick test.
    # Increase problem_size to 4 to test a medium load.
    parameters = {
        "problem_id": "cirq_debug_001",
        "problem_complexity": 100,
        "problem_size": 3,
        "circuit_depth": 1,
    }

    # Test QAOA (change to "VQE" if preferred)
    algorithm_id = "QAOA"

    print(f"Parameters: {parameters}")
    print(f"Algorithm: {algorithm_id}")
    print("---------------------------------------------------")

    # 4. Execute the job directly
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

        # Additional file verification
        if artifact_url:
            # Convert the relative API path to an absolute filesystem path for verification
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
