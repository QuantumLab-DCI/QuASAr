# app/services/hqc_module.py (Corregido)
import random

# --- Imports de los adaptadores ---
from .hqc_backends.base_backend import QuantumBackend
from .hqc_backends.qiskit_adapter import QiskitAdapter
from .hqc_backends.spinq_adapter import SpinqAdapter
from .hqc_backends.tql_adapter import TqlAdapter
# --- Fin Imports ---

def get_backend_adapter(backend_name: str) -> QuantumBackend:
    """
    FÁBRICA (Factory) de Backends Cuánticos.
    
    Recibe el nombre del backend (decidido por el LLM) y devuelve
    una instancia del adaptador correspondiente.
    """
    print(f"⚛️  HQC_Factory: Solicitud para instanciar backend: '{backend_name}'")
    
    # --- INICIO DE LA CORRECCIÓN ---
    # Convertimos a minúsculas para una comparación segura
    backend_name_lower = backend_name.lower()
    # --- FIN DE LA CORRECCIÓN ---

    try:
        # --- INICIO DE LA CORRECCIÓN ---
        if "qiskit" in backend_name_lower:
            return QiskitAdapter()
        
        elif "spinq" in backend_name_lower:
            return SpinqAdapter()
            
        elif "tql" in backend_name_lower:
            return TqlAdapter()
        # --- FIN DE LA CORRECCIÓN ---
            
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
    Función que simula el monitoreo de la era NISQ.
    (Esta función sigue igual).
    """
    metricas = {
        "Qiskit Simulator": {
            "queue_time_sec": random.randint(1, 300),
            "error_rate": random.uniform(0.01, 0.15)
        },
        "SpinQ Simulator": {
            "queue_time_sec": 0, # Es local
            "error_rate": random.uniform(0.05, 0.25)
        },
        "TQL Simulator": {
            "queue_time_sec": random.randint(1, 50),
            "error_rate": random.uniform(0.02, 0.10)
        }
    }
    # print(f"📊 Métricas NISQ monitoreadas: {metricas}") # Comentado
    return metricas