from .base_backend import QuantumBackend
import numpy as np
import matplotlib.pyplot as plt
import os

# Mover los imports que fallan a un bloque 'try'
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
    """

    def __init__(self):
        if not QISKIT_BASE_DISPONIBLE:
            raise ImportError("Dependencias base de Qiskit no encontradas o incompatibles.")
        
        try:
            from qiskit_aer import AerSimulator
            self.aer_backend = AerSimulator()
            algorithm_globals.random_seed = 123
            print("   ...Adaptador Qiskit inicializado (con QAOA y VQE).")
        except Exception as e:
            print(f"HQC_ERROR: Fallo al inicializar el backend de Qiskit Aer. {e}")
            raise ImportError(f"Fallo en Qiskit Aer: {e}")

    def _create_tsp_qubo(self, n, distance_matrix):
        """
        Crea manualmente el programa cuadrático (QUBO) para el TSP.
        Esto reemplaza a la clase 'TravelingSalesperson' que fue eliminada.
        """
        from qiskit_optimization import QuadraticProgram
        
        qp = QuadraticProgram()
        
        # Variables binarias x_ij: ciudad i en la posición j
        # n ciudades, n pasos de tiempo -> n^2 variables
        for i in range(n):
            for j in range(n):
                qp.binary_var(name=f'x_{i}_{j}')
        
        # Función Objetivo: Minimizar distancia total
        # Sum_{i,j} dist(i,j) * Sum_{p} x_{i,p} * x_{j,p+1}
        linear = {}
        quadratic = {}
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    d = distance_matrix[i][j]
                    for p in range(n):
                        next_p = (p + 1) % n
                        # Término cuadrático: x_{i,p} * x_{j,next_p}
                        key = (f'x_{i}_{p}', f'x_{j}_{next_p}')
                        quadratic[key] = d

        qp.minimize(linear=linear, quadratic=quadratic)
        
        # Restricciones (Penalty terms se agregan automáticamente al convertir a Ising,
        # pero aquí definimos las restricciones lineales explícitas)
        
        # 1. Cada ciudad debe visitarse exactamente una vez
        for i in range(n):
            qp.linear_constraint(linear={f'x_{i}_{p}': 1 for p in range(n)}, sense='==', rhs=1, name=f'city_{i}')
            
        # 2. Cada posición de tiempo debe tener exactamente una ciudad
        for p in range(n):
            qp.linear_constraint(linear={f'x_{i}_{p}': 1 for i in range(n)}, sense='==', rhs=1, name=f'time_{p}')
            
        return qp

    def _solve_tsp(self, solver_instance, qp, n_ciudades):
        """
        Función genérica que resuelve un TSP (formato QuadraticProgram) usando el solver.
        """
        from qiskit_optimization.algorithms import MinimumEigenOptimizer
        
        print(f"   ...Problema TSP mapeado a QuadraticProgram (QUBO) manualmente.")

        print("   ...[PRUEBA DE CÓMPUTO] Generando el circuito (Ansatz)...")
        operator, offset = qp.to_ising()
        
        ansatz = None
        if solver_instance.__class__.__name__ == 'QAOA':
            ansatz = solver_instance.construct_circuit(operator)[0]
        elif solver_instance.__class__.__name__ == 'VQE':
            ansatz = solver_instance.ansatz
        
        # --- GENERACIÓN DE EVIDENCIA VISUAL ---
        evidence_path = "No generado"

        if ansatz:
            try:
                base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../data'))
                if not os.path.exists(base_path):
                    os.makedirs(base_path, exist_ok=True)

                img_filename = "qiskit_circuit_evidence.png"
                full_path = os.path.join(base_path, img_filename)

                print(f"   ...[EVIDENCIA] Generando imagen del circuito en: {full_path}")
                # Usar 'mpl' style si está disponible, sino fallback
                ansatz.draw(output='mpl', filename=full_path)
                evidence_path = f"/api/static/{img_filename}"
                
            except Exception as e:
                print(f"   ...WARN: No se pudo generar imagen del circuito: {e}")
        else:
            print("   ...No se pudo extraer el circuito (ansatz) del solver.")
        # --- FIN EVIDENCIA ---

        optimizer = MinimumEigenOptimizer(solver_instance)

        print(f"   ...Ejecutando {solver_instance.__class__.__name__} en simulador Aer...")
        result = optimizer.solve(qp)
        
        # Interpretación simple del resultado (x_i_p = 1)
        # Como lo hicimos manual, parseamos las variables activas
        ruta_raw = [v.name for v in result.variables if v.as_tuple()[1] > 0.9]
        
        return {
            "backend": "Qiskit",
            "algoritmo": solver_instance.__class__.__name__,
            "problema": f"TSP de {n_ciudades} nodos (QUBO Manual)",
            "variables_activas": ruta_raw,
            "costo_optimo": result.fval,
            "evidencia_visual": evidence_path
        }

    def execute_job(self, algoritmo: str, params: dict) -> dict:
        print(f"⚛️  QiskitAdapter: Ejecutando trabajo (Algoritmo: {algoritmo.upper()}).")
        
        try:
            from qiskit_algorithms import QAOA, VQE
            from qiskit_algorithms.optimizers import SLSQP
            from qiskit.circuit.library import TwoLocal
        except ImportError as e:
            msg = f"Faltan dependencias de Qiskit: {e}"
            print(f"   ...ERROR: {msg}")
            return {"error": msg}

        # Definir problema (3 ciudades)
        n_ciudades = 3
        distancias = np.array([
            [0, 10, 25],
            [10, 0, 15],
            [25, 15, 0]
        ])
        
        # Crear QUBO manualmente
        qp = self._create_tsp_qubo(n_ciudades, distancias)
        
        solver = None
        if "QAOA" in algoritmo.upper():
            print("   ...Instanciando solver QAOA...")
            solver = QAOA(optimizer=SLSQP(), reps=1, quantum_instance=self.aer_backend)
            
        elif "VQE" in algoritmo.upper():
            print("   ...Instanciando solver VQE...")
            # Num qubits = n^2 para TSP con encoding One-Hot
            num_qubits = n_ciudades * n_ciudades 
            ansatz = TwoLocal(num_qubits, 'ry', 'cz', reps=1)
            solver = VQE(optimizer=SLSQP(), ansatz=ansatz, quantum_instance=self.aer_backend)
            
        else:
            msg = f"Algoritmo {algoritmo} no soportado en QiskitAdapter."
            print(f"   ...ERROR: {msg}")
            return {"error": msg}

        return self._solve_tsp(solver, qp, n_ciudades)