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
    Adaptador específico para Qiskit (Modernizado para Primitivas).
    Implementa la lógica real de optimización de rutas usando QAOA o VQE.
    """

    def __init__(self):
        if not QISKIT_BASE_DISPONIBLE:
            raise ImportError("Dependencias base de Qiskit no encontradas o incompatibles.")
        
        try:
            # --- CORRECCIÓN: Usar Primitivas AER en lugar de backend crudo ---
            from qiskit_aer.primitives import Sampler, Estimator
            
            # Instanciamos las primitivas locales de alto rendimiento (Aer)
            self.sampler = Sampler() 
            self.estimator = Estimator()
            
            algorithm_globals.random_seed = 123
            print("   ...Adaptador Qiskit inicializado (con Primitivas Aer Sampler/Estimator).")
            
        except Exception as e:
            print(f"HQC_ERROR: Fallo al inicializar primitivas de Qiskit Aer. {e}")
            # Fallback a primitivas estándar si Aer falla
            try:
                from qiskit.primitives import Sampler, Estimator
                self.sampler = Sampler()
                self.estimator = Estimator()
                print("   ...Fallback: Usando Primitivas de referencia (Reference Primitives).")
            except:
                raise ImportError(f"Fallo crítico en Qiskit: {e}")

    def _create_tsp_qubo(self, n, distance_matrix):
        """
        Crea manualmente el programa cuadrático (QUBO) para el TSP.
        """
        from qiskit_optimization import QuadraticProgram
        
        qp = QuadraticProgram()
        
        # Variables binarias x_ij: ciudad i en la posición j
        for i in range(n):
            for j in range(n):
                qp.binary_var(name=f'x_{i}_{j}')
        
        # Función Objetivo: Minimizar distancia total
        linear = {}
        quadratic = {}
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    d = distance_matrix[i][j]
                    for p in range(n):
                        next_p = (p + 1) % n
                        key = (f'x_{i}_{p}', f'x_{j}_{next_p}')
                        quadratic[key] = d

        qp.minimize(linear=linear, quadratic=quadratic)
        
        # Restricciones
        for i in range(n):
            qp.linear_constraint(linear={f'x_{i}_{p}': 1 for p in range(n)}, sense='==', rhs=1, name=f'city_{i}')
        for p in range(n):
            qp.linear_constraint(linear={f'x_{i}_{p}': 1 for i in range(n)}, sense='==', rhs=1, name=f'time_{p}')
            
        return qp

    def _solve_tsp(self, solver_instance, qp, n_ciudades):
        """
        Función genérica que resuelve un TSP usando el solver (QAOA/VQE).
        """
        from qiskit_optimization.algorithms import MinimumEigenOptimizer
        
        print(f"   ...Problema TSP mapeado a QuadraticProgram (QUBO).")

        # --- GENERACIÓN DE EVIDENCIA VISUAL (Circuito) ---
        print("   ...[PRUEBA DE CÓMPUTO] Extrayendo circuito (Ansatz) para evidencia...")
        evidence_path = "No generado"
        try:
            # Necesitamos el operador Ising para construir el circuito de prueba
            operator, offset = qp.to_ising()
            
            ansatz = None
            # Lógica específica para extraer el circuito dependiendo del algoritmo
            if hasattr(solver_instance, 'ansatz') and solver_instance.ansatz is not None:
                ansatz = solver_instance.ansatz
            elif hasattr(solver_instance, 'construct_circuit'):
                # QAOA moderno suele construir el circuito bajo demanda
                ansatz = solver_instance.construct_circuit(operator, [1.0, 1.0])[0] # params dummy

            if ansatz:
                base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../data'))
                if not os.path.exists(base_path):
                    os.makedirs(base_path, exist_ok=True)

                img_filename = "qiskit_circuit_evidence.png"
                full_path = os.path.join(base_path, img_filename)
                
                # Dibujar y guardar
                ansatz.draw(output='mpl', filename=full_path)
                evidence_path = f"/api/static/{img_filename}"
                print(f"   ...[EVIDENCIA] Circuito guardado en: {full_path}")
            else:
                print("   ...Info: No se pudo aislar el ansatz para graficar (pero la ejecución continúa).")
                
        except Exception as e:
            print(f"   ...WARN Visualización: {e}")
        # --- FIN EVIDENCIA ---

        optimizer = MinimumEigenOptimizer(solver_instance)

        print(f"   ...Ejecutando optimización con {solver_instance.__class__.__name__}...")
        result = optimizer.solve(qp)
        
        # Parseo básico de resultado
        ruta_raw = [v.name for v in result.variables if v.as_tuple()[1] > 0.9]
        
        return {
            "backend": "Qiskit (Aer Primitives)",
            "algoritmo": solver_instance.__class__.__name__,
            "problema": f"TSP de {n_ciudades} nodos",
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
            msg = f"Faltan dependencias de Qiskit Algorithms: {e}"
            print(f"   ...ERROR: {msg}")
            return {"error": msg}

        # Definir problema (3 ciudades)
        n_ciudades = 3
        distancias = np.array([
            [0, 10, 25],
            [10, 0, 15],
            [25, 15, 0]
        ])
        
        qp = self._create_tsp_qubo(n_ciudades, distancias)
        
        solver = None
        if "QAOA" in algoritmo.upper():
            print("   ...Configurando QAOA con Sampler...")
            # --- CORRECCIÓN CRÍTICA: Usar 'sampler' en lugar de 'quantum_instance' ---
            solver = QAOA(sampler=self.sampler, optimizer=SLSQP(), reps=1)
            
        elif "VQE" in algoritmo.upper():
            print("   ...Configurando VQE con Estimator...")
            num_qubits = n_ciudades * n_ciudades 
            ansatz = TwoLocal(num_qubits, 'ry', 'cz', reps=1)
            # --- CORRECCIÓN CRÍTICA: Usar 'estimator' en lugar de 'quantum_instance' ---
            solver = VQE(estimator=self.estimator, optimizer=SLSQP(), ansatz=ansatz)
            
        else:
            msg = f"Algoritmo {algoritmo} no soportado en QiskitAdapter."
            return {"error": msg}

        return self._solve_tsp(solver, qp, n_ciudades)