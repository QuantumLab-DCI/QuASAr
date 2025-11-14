# app/services/hqc_backends/qiskit_adapter.py
from .base_backend import QuantumBackend
import numpy as np

# Dependencias cuánticas específicas de Qiskit
try:
    from qiskit import Aer
    from qiskit.algorithms import QAOA
    from qiskit.utils import QuantumInstance
    from qiskit_optimization.algorithms import MinimumEigenOptimizer
    from qiskit_optimization import QuadraticProgram
    from qiskit_optimization.problems import TravelingSalesperson
    QISKIT_DISPONIBLE = True
except ImportError:
    print("HQC_ERROR: Qiskit o Qiskit_Optimization no están instalados.")
    print("HQC_ERROR: Ejecuta: pip install qiskit qiskit_optimization")
    QISKIT_DISPONIBLE = False

class QiskitAdapter(QuantumBackend):
    """
    Adaptador específico para Qiskit.
    Implementa la lógica real de optimización de rutas usando QAOA.
    """

    def __init__(self):
        if not QISKIT_DISPONIBLE:
            raise ImportError("Dependencias de Qiskit no encontradas.")
        
        # Configurar la instancia de Qiskit (simulador)
        self.q_instance = QuantumInstance(
            backend=Aer.get_backend('aer_simulator_statevector'),
            seed_simulator=123,
            seed_transpiler=123
        )
        print("   ...Adaptador Qiskit inicializado.")

    def _solve_tsp_qaoa(self, params: dict) -> dict:
        """
        Lógica de negocio: Resuelve un problema de TSP (Optimización de Rutas) con QAOA.
        """
        # 1. Definir el problema (Toy problem de 3 nodos)
        n_ciudades = 3
        distancias = np.array([
            [0, 10, 25],
            [10, 0, 15],
            [25, 15, 0]
        ])
        
        print(f"   ...Definiendo Problema TSP con {n_ciudades} nodos.")
        tsp = TravelingSalesperson(distancias)
        qp = tsp.to_quadratic_program()
        print(f"   ...Problema mapeado a QuadraticProgram (QUBO).")

        # 2. Configurar el optimizador QAOA
        qaoa_mes = QAOA(quantum_instance=self.q_instance, reps=1) 
        qaoa_optimizer = MinimumEigenOptimizer(qaoa_mes)

        # 3. Resolver
        print(f"   ...Ejecutando QAOA en simulador Aer...")
        result = qaoa_optimizer.solve(qp)
        
        # 4. Interpretar y devolver
        ruta_optima = tsp.interpret(result)
        
        return {
            "backend": "Qiskit (QAOA)",
            "problema": f"TSP de {n_ciudades} nodos",
            "ruta_optima": ruta_optima,
            "distancia_optima": tsp.get_optimal_cost(),
        }

    def execute_job(self, algoritmo: str, params: dict) -> dict:
        print(f"⚛️  QiskitAdapter: Ejecutando trabajo (Algoritmo: {algoritmo.upper()}).")
        
        if "QAOA" in algoritmo.upper() or "VQE" in algoritmo.upper():
            # Para la PoC, ambos algoritmos de optimización llaman a la misma función
            return self._solve_tsp_qaoa(params)
        else:
            msg = f"Algoritmo {algoritmo} no soportado en QiskitAdapter."
            print(f"   ...ERROR: {msg}")
            return {"error": msg}