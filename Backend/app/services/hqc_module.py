# app/services/hqc_module.py
import random
from .hqc_backends.base_backend import QuantumBackend
from .hqc_backends.qiskit_adapter import QiskitAdapter
from .hqc_backends.cirq_adapter import CirqAdapter

def get_backend_adapter(backend_name: str) -> QuantumBackend:
    """ Factory for quantum backends. """
    print(f"⚛️  HQC_Factory: Solicitud para instanciar backend: '{backend_name}'")
    backend_name_lower = backend_name.lower()
    try:
        if "qiskit" in backend_name_lower:
            return QiskitAdapter()
        elif "cirq" in backend_name_lower:
            return CirqAdapter()
        else:
            return None
    except Exception as e:
        print(f"   ...ERROR FACTORY: Falla inesperada al instanciar '{backend_name}'. {e}")
        return None

def monitor_backends():
    """
    HIGH-ENTROPY SIMULATION (thesis-defense strategy).
    Objective: Break the LLM's deterministic bias by making the metrics fluctuate.
    
    1. Qiskit: Behaves as the 'Safe Harbor' (stable).
    2. Cirq: Behaves as the 'Weak Link' (sometimes fast, sometimes overloaded).
    3. Algorithm: Inject a random suggestion to force VQE.
    """
    
    # --- 1. QISKIT (The Stable Option) ---
    # Maintain a consistent and tolerable queue.
    # 4 to 8 seconds is acceptable for accuracy, but loses to Cirq when Cirq is at 0 seconds.
    qiskit_queue = int(random.uniform(4, 8)) 
    qiskit_error = 0.002 # Very accurate (0.2%)

    # --- 2. CIRQ (The Unstable Option) ---
    # WIDE range (0 to 25 seconds).
    # - At 0-3 seconds, the LLM will select Cirq (speed).
    # - At 10-25 seconds, the LLM will select Qiskit (avoids congestion).
    # This produces an approximately 50% alternation in decisions.
    cirq_queue = int(random.uniform(0, 25)) 
    cirq_error = 0.08  # Noisy (8%)

    # --- 3. ALGORITHM SUGGESTION (Novelty Factor) ---
    # Inject a context signal so the LLM considers VQE
    sugerencia_algo = random.choice(["QAOA", "VQE", "QAOA", "VQE"]) 

    metricas = {
        "Qiskit Simulator": {
            "queue_time_sec": qiskit_queue,
            "error_rate": qiskit_error,
            "status": "ONLINE"
        },
        "Cirq Simulator": {
            "queue_time_sec": cirq_queue,
            "error_rate": cirq_error,
            "status": "ONLINE"
        },
        # Additional metadata for influencing the LLM
        "entorno_cuantico": {
            "estado_decoherencia": "ALTO" if sugerencia_algo == "QAOA" else "BAJO",
            "sugerencia_optimizacion": sugerencia_algo
        }
    }
    
    print(f"📊 [MONITOR CAÓTICO] Qiskit({qiskit_queue}s) vs Cirq({cirq_queue}s) | Sugerencia: {sugerencia_algo}")
    return metricas
