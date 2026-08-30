import random

from .hqc_backends.base_backend import QuantumBackend
from .hqc_backends.cirq_adapter import CirqAdapter
from .hqc_backends.qiskit_adapter import QiskitAdapter


def get_backend_adapter(backend_name: str) -> QuantumBackend | None:
    """Instantiate the adapter selected by the adaptation plan."""
    print(f"HYBRID_QUANTUM_SERVICE: Instantiating backend '{backend_name}'.")
    try:
        normalized_name = backend_name.lower()
        if "qiskit" in normalized_name:
            return QiskitAdapter()
        if "cirq" in normalized_name:
            return CirqAdapter()
        return None
    except Exception as error:
        print(
            "HYBRID_QUANTUM_SERVICE_ERROR: Could not instantiate "
            f"'{backend_name}': {error}"
        )
        return None


def monitor_backends() -> dict:
    """Generate variable NISQ backend observations for adaptation analysis."""
    qiskit_queue_time = int(random.uniform(4, 8))
    cirq_queue_time = int(random.uniform(0, 25))
    suggested_algorithm = random.choice(["QAOA", "VQE", "QAOA", "VQE"])
    metrics = {
        "Qiskit Simulator": {
            "queue_time_seconds": qiskit_queue_time,
            "error_rate": 0.002,
            "status": "ONLINE",
        },
        "Cirq Simulator": {
            "queue_time_seconds": cirq_queue_time,
            "error_rate": 0.08,
            "status": "ONLINE",
        },
        "quantum_runtime": {
            "decoherence_level": "HIGH" if suggested_algorithm == "QAOA" else "LOW",
            "suggested_algorithm": suggested_algorithm,
        },
    }
    print(
        "BACKEND_MONITOR: "
        f"Qiskit({qiskit_queue_time}s), Cirq({cirq_queue_time}s), "
        f"suggested algorithm={suggested_algorithm}."
    )
    return metrics
