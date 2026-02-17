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
        print(f"   ...ERROR FACTORY: Falla inesperada al instanciar '{backend_name}'. {e}")
        return None

def monitor_backends():
    """
    SIMULACIÓN DE ALTA ENTROPÍA (Estrategia para Defensa).
    Objetivo: Romper el sesgo determinista del LLM haciendo que los métricas 'bailen'.
    
    1. Qiskit: Se comporta como el 'Puerto Seguro' (Estable).
    2. Cirq: Se comporta como el 'Eslabón Débil' (A veces rápido, a veces colapsado).
    3. Algoritmo: Se inyecta una sugerencia aleatoria para forzar VQE.
    """
    
    # --- 1. QISKIT (El Estable) ---
    # Mantenemos una cola constante y tolerable.
    # 4 a 8 segundos es aceptable para precisión, pero pierde contra Cirq cuando Cirq está en 0s.
    qiskit_queue = int(random.uniform(4, 8)) 
    qiskit_error = 0.002 # Muy preciso (0.2%)

    # --- 2. CIRQ (El Inestable) ---
    # Rango AMPLIO (0 a 25s).
    # - Si sale 0-3s: El LLM elegirá Cirq (Rapidez).
    # - Si sale 10-25s: El LLM elegirá Qiskit (Evitar congestión).
    # Esto garantiza una alternancia de ~50% en las decisiones.
    cirq_queue = int(random.uniform(0, 25)) 
    cirq_error = 0.08  # Ruidoso (8%)

    # --- 3. SUGERENCIA DE ALGORITMO (Factor de Novedad) ---
    # Inyectamos una señal de contexto para que el LLM considere VQE
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
        # Metadata extra para influenciar al LLM
        "entorno_cuantico": {
            "estado_decoherencia": "ALTO" if sugerencia_algo == "QAOA" else "BAJO",
            "sugerencia_optimizacion": sugerencia_algo
        }
    }
    
    print(f"📊 [MONITOR CAÓTICO] Qiskit({qiskit_queue}s) vs Cirq({cirq_queue}s) | Sugerencia: {sugerencia_algo}")
    return metricas