from .base_backend import QuantumBackend
import numpy as np

# Mover los imports que fallan a un bloque 'try'
# y mantener solo los imports seguros en el nivel superior.
try:
    from qiskit_algorithms.utils import algorithm_globals
    QISKIT_BASE_DISPONIBLE = True
except ImportError:
    print("HQC_WARN: qiskit-algorithms no está instalado o no es compatible.")
    QISKIT_BASE_DISPONIBLE = False

class QiskitAdapter(QuantumBackend):
    """
    Adaptador específico para Qiskit.
    Implementa la lógica real de optimización de rutas usando QAOA o VQE.
    Los imports se realizan dentro de los métodos para permitir
    que la app se inicie incluso si Qiskit no está instalado.
    """

    def __init__(self):
        if not QISKIT_BASE_DISPONIBLE:
            raise ImportError("Dependencias base de Qiskit no encontradas o incompatibles.")
        
        # Mover los imports al constructor
        try:
            from qiskit_aer import AerSimulator
            self.aer_backend = AerSimulator()
            algorithm_globals.random_seed = 123
            print("   ...Adaptador Qiskit inicializado (con QAOA y VQE).")
        except Exception as e:
            print(f"HQC_ERROR: Fallo al inicializar el backend de Qiskit Aer. {e}")
            raise ImportError(f"Fallo en Qiskit Aer: {e}")

    def _get_tsp_problem(self) -> ('TravelingSalesperson', int):
        """Función auxiliar para crear el problema de TSP."""
        # Importar aquí
        from qiskit_optimization.problems import TravelingSalesperson
        
        n_ciudades = 3
        distancias = np.array([
            [0, 10, 25],
            [10, 0, 15],
            [25, 15, 0]
        ])
        print(f"   ...Definiendo Problema TSP con {n_ciudades} nodos.")
        tsp = TravelingSalesperson(distancias)
        return tsp, n_ciudades

    def _solve_tsp(self, solver_instance, tsp_problem):
        """
        Función genérica que resuelve un TSP usando el solver (QAOA o VQE)
        que le pasen como argumento.
        """
        # Importar aquí
        from qiskit_optimization.algorithms import MinimumEigenOptimizer
        
        qp = tsp_problem.to_quadratic_program()
        print(f"   ...Problema mapeado a QuadraticProgram (QUBO).")

        print("   ...[PRUEBA DE CÓMPUTO] Generando el circuito (Ansatz)...")
        operator, offset = qp.to_ising()
        
        ansatz = None
        # Usamos nombres de clase como strings para evitar errores de import si las clases no están cargadas globalmente
        if solver_instance.__class__.__name__ == 'QAOA':
            ansatz = solver_instance.construct_circuit(operator)[0]
        elif solver_instance.__class__.__name__ == 'VQE':
            ansatz = solver_instance.ansatz
            
        if ansatz:
            try:
                print(f"   ...Circuito (Ansatz) construido ({ansatz.num_qubits} qubits, {ansatz.depth()} profundidad):\n")
                # Imprimir el circuito en formato texto para los logs
                print(ansatz.draw(output='text', fold=-1))
                print("\n   ...[PRUEBA DE CÓMPUTO] Fin del circuito.")
            except Exception as e:
                print(f"   ...No se pudo dibujar el circuito: {e}")
        else:
            print("   ...No se pudo extraer el circuito (ansatz) del solver.")

        optimizer = MinimumEigenOptimizer(solver_instance)

        print(f"   ...Ejecutando {solver_instance.__class__.__name__} en simulador Aer...")
        result = optimizer.solve(qp)
        
        ruta_optima = tsp_problem.interpret(result)
        
        return {
            "backend": "Qiskit",
            "algoritmo": solver_instance.__class__.__name__,
            "problema": f"TSP de {tsp_problem.dim} nodos",
            "ruta_optima": ruta_optima,
            "distancia_optima": tsp_problem.get_optimal_cost(),
        }

    def execute_job(self, algoritmo: str, params: dict) -> dict:
        print(f"⚛️  QiskitAdapter: Ejecutando trabajo (Algoritmo: {algoritmo.upper()}).")
        
        # Importar aquí
        try:
            from qiskit_algorithms import QAOA, VQE
            from qiskit_algorithms.optimizers import SLSQP
            from qiskit.circuit.library import TwoLocal
        except ImportError as e:
            msg = f"Faltan dependencias de Qiskit (QAOA/VQE) o son incompatibles: {e}"
            print(f"   ...ERROR: {msg}")
            return {"error": msg}

        tsp_problem, num_nodos = self._get_tsp_problem()
        
        solver = None
        if "QAOA" in algoritmo.upper():
            print("   ...Instanciando solver QAOA...")
            solver = QAOA(optimizer=SLSQP(), reps=1, quantum_instance=self.aer_backend)
            
        elif "VQE" in algoritmo.upper():
            print("   ...Instanciando solver VQE...")
            # VQE necesita una "forma variacional" (el circuito/ansatz)
            num_qubits_qubo = num_nodos * num_nodos
            ansatz = TwoLocal(num_qubits_qubo, 'ry', 'cz', reps=1)
            solver = VQE(optimizer=SLSQP(), ansatz=ansatz, quantum_instance=self.aer_backend)
            
        else:
            msg = f"Algoritmo {algoritmo} no soportado en QiskitAdapter."
            print(f"   ...ERROR: {msg}")
            return {"error": msg}

        return self._solve_tsp(solver, tsp_problem)