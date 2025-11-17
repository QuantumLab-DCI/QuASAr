# app/services/hqc_module.py (Actualizado para Qiskit y Cirq)
import random

# --- Imports de los adaptadores ---
from .hqc_backends.base_backend import QuantumBackend
from .hqc_backends.qiskit_adapter import QiskitAdapter
from .hqc_backends.cirq_adapter import CirqAdapter  # <--- NUEVO
# --- Fin Imports ---

def get_backend_adapter(backend_name: str) -> QuantumBackend:
    """
    FÁBRICA (Factory) de Backends Cuánticos.
    """
    print(f"⚛️  HQC_Factory: Solicitud para instanciar backend: '{backend_name}'")

    backend_name_lower = backend_name.lower()

    try:
        if "qiskit" in backend_name_lower:
            return QiskitAdapter()

        elif "cirq" in backend_name_lower:  # <--- NUEVO
            return CirqAdapter()

        else:
            print(f"   ...ERROR: No se encontró un adaptador para '{backend_name}'.")
            return None

    except ImportError as e:
        print(f"   ...ERROR: Faltan dependencias para '{backend_name}'. {e}")
        return None
    except Exception as e:
        print(f"   ...ERROR: Falla inesperada al instanciar '{backend_name}'. {e}")
        return None

def monitor_backends():
    """
    Simula el monitoreo NISQ para Qiskit y Cirq.
    """
    metricas = {
        "Qiskit Simulator": {  # <--- MANTENIDO
            "queue_time_sec": random.randint(1, 300),
            "error_rate": random.uniform(0.01, 0.15)
        },
        "Cirq Simulator": {  # <--- NUEVO
            "queue_time_sec": random.randint(1, 50), # Simulamos que es rápido
            "error_rate": random.uniform(0.02, 0.10)
        }
    }
    print(f"📊 Métricas NISQ monitoreadas: {metricas}")
    return metricas