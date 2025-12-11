# app/services/hqc_module.py
import random

# --- Imports de los adaptadores ---
from .hqc_backends.base_backend import QuantumBackend
from .hqc_backends.qiskit_adapter import QiskitAdapter
from .hqc_backends.cirq_adapter import CirqAdapter
# --- Fin Imports ---

def get_backend_adapter(backend_name: str) -> QuantumBackend:
    """
    FÁBRICA (Factory) de Backends Cuánticos.
    Instancia el adaptador correcto según el nombre solicitado por el planificador.
    """
    print(f"⚛️  HQC_Factory: Solicitud para instanciar backend: '{backend_name}'")

    backend_name_lower = backend_name.lower()

    try:
        if "qiskit" in backend_name_lower:
            return QiskitAdapter()

        elif "cirq" in backend_name_lower:
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
    Simula métricas NISQ con un TRADE-OFF claro para forzar la variabilidad en la demo:
    
    1. Qiskit Simulator (Perfil Cloud): 
       - PRO: Muy preciso (Error bajo ~0.1% - 1.5%)
       - CONTRA: Lento (Cola de nube variable, simula congestión)
       
    2. Cirq Simulator (Perfil Local / SpinQ Gemini): 
       - PRO: Inmediato (Cola ~0s - 2s)
       - CONTRA: Ruidoso (Simula dispositivo pequeño con alta decoherencia, Error ~5% - 12%)
    """
    
    # --- 1. PERFIL QISKIT (El "Experto Lento") ---
    # Simula cola en la nube: A veces rápida (5s), a veces saturada (60s)
    qiskit_queue = int(random.choice([5, 15, 45, 60])) 
    # Error: Muy bajo y estable (Simulador potente o QPU High-Fidelity)
    qiskit_error = round(random.uniform(0.001, 0.015), 4) # 0.1% a 1.5%

    # --- 2. PERFIL CIRQ/SPINQ (El "Rápido Ruidoso") ---
    # Simula ejecución local: Siempre rápida
    cirq_queue = int(random.uniform(0, 2))
    # Error: Alto y variable (Simulando decoherencia de un dispositivo pequeño tipo Gemini)
    cirq_error = round(random.uniform(0.05, 0.12), 4) # 5% a 12%

    # Inyectar "Eventos de Saturación Extrema" ocasionales en la nube (5% probabilidad)
    if random.random() < 0.05:
        print("   ...[MONITOR] ⚠️ ALERTA: Pico de congestión en IBM Quantum Cloud")
        qiskit_queue += 120 # La cola explota a +2 minutos

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
    
    # Formato legible para el log de la consola
    print(f"📊 [MONITOR] Métricas NISQ Actualizadas:")
    print(f"   > Qiskit (Cloud): Cola {qiskit_queue}s | Error {qiskit_error:.2%}")
    print(f"   > Cirq   (Local): Cola {cirq_queue}s  | Error {cirq_error:.2%}")
    
    return metricas