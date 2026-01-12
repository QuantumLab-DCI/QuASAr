# app/services/hqc_module.py
import random
from .hqc_backends.base_backend import QuantumBackend
from .hqc_backends.qiskit_adapter import QiskitAdapter
from .hqc_backends.cirq_adapter import CirqAdapter

def get_backend_adapter(backend_name: str) -> QuantumBackend:
    """ FÁBRICA (Factory) de Backends Cuánticos. """
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
        print(f"   ...ERROR: Falla inesperada al instanciar '{backend_name}'. {e}")
        return None

def monitor_backends():
    """
    Simulación REALISTA y EQUILIBRADA (Alineada con Tesis).
    Genera un trade-off real para que el Agente decida según el SLA.
    """
    
    # --- 1. QISKIT (Nube / Alta Fidelidad) ---
    # Tiempo: Variable pero tolerable (3 a 10 seg). 
    # Suficientemente rápido para ser considerado, suficientemente lento para perder en "Rapidez".
    qiskit_queue = int(random.uniform(3, 10)) 
    
    # Error: Muy bajo (Su gran ventaja)
    qiskit_error = round(random.uniform(0.001, 0.005), 4)

    # --- 2. CIRQ (Local / Ruidoso) ---
    # Tiempo: Muy rápido (0 a 2 seg).
    cirq_queue = int(random.uniform(0, 2))
    
    # Error: Alto (Su gran desventaja)
    cirq_error = round(random.uniform(0.08, 0.15), 4)

    # --- Factor de Caos (Opcional) ---
    # 10% de probabilidad de que la nube esté lenta, forzando un cambio a Cirq incluso en Alta Demanda
    if random.random() < 0.10:
        qiskit_queue += 20 
        print("   ...[MONITOR] ☁️ Variabilidad: La nube de Qiskit está congestionada.")

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
        }
    }
    
    print(f"📊 [MONITOR] Métricas: Qiskit ({qiskit_queue}s, Err {qiskit_error}) vs Cirq ({cirq_queue}s, Err {cirq_error})")
    return metricas