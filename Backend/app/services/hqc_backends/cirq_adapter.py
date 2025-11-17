# app/services/hqc_backends/cirq_adapter.py (Placeholder Semántico)
from .base_backend import QuantumBackend

try:
    import cirq
    CIRK_DISPONIBLE = True
except ImportError:
    print("HQC_WARN: Cirq no está instalado. El CirqAdapter no funcionará si se selecciona.")
    print("HQC_WARN: Ejecuta: pip install cirq")
    CIRK_DISPONIBLE = False

class CirqAdapter(QuantumBackend):
    """
    Adaptador específico para Cirq/TensorFlow Quantum.
    Devuelve un placeholder SEMÁNTICAMENTE CORRECTO (un resultado de TSP)
    para la PoC.
    """

    def __init__(self):
        if not CIRK_DISPONIBLE:
            raise ImportError("Dependencias de Cirq no encontradas.")
        print("   ...Adaptador Cirq inicializado.")

    def execute_job(self, algoritmo: str, params: dict) -> dict:
        print(f"⚛️  CirqAdapter: Ejecutando trabajo (Algoritmo: {algoritmo.upper()}).")

        if "QAOA" in algoritmo.upper() or "VQE" in algoritmo.upper():
            print("   ...Lógica QAOA/VQE no implementada en Cirq/TFQ. Devolviendo resultado de optimización simulado (PoC).")
            # Devolvemos un resultado de optimización FALSO pero semánticamente correcto
            return {
                "backend": "Cirq (Simulado)",
                "algoritmo": algoritmo.upper(),
                "info": "Ejecución simulada (placeholder de optimización) para PoC.",
                "ruta_optima": [0, 1, 2, 0], # Ruta simulada
                "distancia_optima": 50.0,
            }
        else:
            msg = f"Algoritmo {algoritmo} no soportado en CirqAdapter."
            print(f"   ...ERROR: {msg}")
            return {"error": msg}