# app/services/hqc_module.py (Actualizado con Perfiles NISQ Realistas)
import random

# --- Imports de los adaptadores ---
from .hqc_backends.base_backend import QuantumBackend
from .hqc_backends.qiskit_adapter import QiskitAdapter
from .hqc_backends.cirq_adapter import CirqAdapter
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
    Simula el monitoreo NISQ con perfiles realistas.
    - Qiskit (Cloud simulado): Cola variable, error moderado.
    - Cirq (Simulador local): Cola casi nula, error bajo (simulación ideal) o inyectado.
    """
    
    # 1. Perfil IBM Quantum (Qiskit)
    # Simula un servicio en la nube congestionado
    # Cola: Normal (10s) a Saturada (300s)
    qiskit_queue = max(1, int(random.gauss(60, 20))) # Media 60s, Desviación 20s
    # Error: Típico de dispositivo NISQ real (IBM Eagle/Osprey) ~1-3% por CNOT profunda
    qiskit_error = min(0.5, max(0.001, random.gauss(0.02, 0.005))) # Media 2%

    # 2. Perfil Google Cirq (Simulador Local/TFQ)
    # Simula ejecución local o en cluster dedicado
    # Cola: Muy rápida, solo latencia de red/carga
    cirq_queue = max(0, int(random.gauss(2, 1))) # Media 2s
    # Error: Simuladores suelen ser "noiseless" a menos que se inyecte ruido.
    # Vamos a simular que es un "Simulador con Modelo de Ruido"
    cirq_error = min(0.5, max(0.001, random.gauss(0.005, 0.002))) # Media 0.5% (Más preciso por ser simulador)

    # Inyectar "Eventos de Saturación" ocasionales (10% probabilidad)
    if random.random() < 0.1:
        print("   ...[MONITOR] ⚠️ Detectado pico de carga en IBM Quantum")
        qiskit_queue += 200 # Cola explota

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
    
    # Formato legible para el log
    print(f"📊 Métricas NISQ (Simuladas):")
    print(f"   - Qiskit: Cola {qiskit_queue}s, Error {qiskit_error:.2%}")
    print(f"   - Cirq:   Cola {cirq_queue}s, Error {cirq_error:.2%}")
    
    return metricas