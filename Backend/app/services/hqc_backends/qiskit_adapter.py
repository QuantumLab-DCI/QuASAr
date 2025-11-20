# app/services/hqc_backends/qiskit_adapter.py (Versión Corregida para Qiskit Aer 0.15+ / Primitivas V2)
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
    Adaptador específico para Qiskit (Modernizado para Primitivas V2).
    Implementa la lógica real de optimización de rutas usando QAOA o VQE.
    Soporta Adaptación de Carga de Trabajo (Tamaño y Profundidad variables).
    """

    def __init__(self):
        if not QISKIT_BASE_DISPONIBLE:
            raise ImportError("Dependencias base de Qiskit no encontradas o incompatibles.")
        
        try:
            # --- CORRECCIÓN CRÍTICA: Usar Primitivas V2 ---
            # Qiskit Algorithms moderno espera la interfaz V2 (Pubs)
            from qiskit_aer.primitives import SamplerV2, EstimatorV2
            
            # Instanciamos las primitivas V2
            self.sampler = SamplerV2() 
            self.estimator = EstimatorV2()
            
            # Configuración de semilla (para V2 se maneja distinto, pero mantenemos esto para utils)
            algorithm_globals.random_seed = 123
            print("   ...Adaptador Qiskit inicializado (con Primitivas Aer V2).")
            
        except ImportError:
            # Fallback si el usuario tiene una versión muy antigua de Aer (aunque el log dice que tiene la 0.15)
            print("   ...WARN: Primitivas V2 no encontradas. Intentando con V1 (puede fallar)...")
            from qiskit_aer.primitives import Sampler, Estimator
            self.sampler = Sampler()
            self.estimator = Estimator()
        except Exception as e:
            raise ImportError(f"Fallo crítico al inicializar Qiskit Aer: {e}")

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
        
        # Restricciones (Constraints explícitos)
        for i in range(n):
            qp.linear_constraint(linear={f'x_{i}_{p}': 1 for p in range(n)}, sense='==', rhs=1, name=f'city_{i}')
        for p in range(n):
            qp.linear_constraint(linear={f'x_{i}_{p}': 1 for i in range(n)}, sense='==', rhs=1, name=f'time_{p}')
            
        return qp

    def _solve_tsp(self, solver_instance, qp, n_ciudades):
        """
        Función genérica que resuelve un TSP.
        CORREGIDA: Usa SamplingVQE (con Sampler) en lugar de VQE (con Estimator) para obtener bitstrings.
        """
        from qiskit_optimization.algorithms import MinimumEigenOptimizer
        from qiskit_optimization.converters import QuadraticProgramToQubo 
        from qiskit.circuit.library import QAOAAnsatz
        from qiskit import transpile
        # [CAMBIO CRÍTICO] Importamos SamplingVQE
        from qiskit_algorithms import SamplingVQE 
        
        print(f"   ...Problema TSP mapeado a QuadraticProgram (Constraints explícitos).")

        # 1. CONVERSIÓN A QUBO
        print("   ...[CONVERSIÓN] Transformando restricciones a penalizaciones (QUBO)...")
        conv = QuadraticProgramToQubo()
        qubo = conv.convert(qp)
        
        # 2. OBTENER OPERADOR ISING
        operator, offset = qubo.to_ising()
        print(f"      -> Operador Ising generado: {operator.num_qubits} Qubits.")

        # 3. PREPARAR SOLVER
        real_solver = solver_instance
        
        if isinstance(solver_instance, dict) and solver_instance.get("type") == "QAOA":
            print("   ...[QAOA BUILDER] Construyendo circuito QAOAAnsatz explícito...")
            reps = solver_instance["reps"]
            
            # Construir Ansatz
            raw_ansatz = QAOAAnsatz(cost_operator=operator, reps=reps, name="QAOA")
            
            # Transpilar para Aer
            print("      -> Transpilando circuito (resolviendo PauliEvolution)...")
            ansatz = transpile(raw_ansatz, basis_gates=['rx', 'ry', 'rz', 'cx', 'h'])

            # [CAMBIO CRÍTICO] Usamos SamplingVQE con el Sampler
            # SamplingVQE es necesario para que MinimumEigenOptimizer pueda leer la solución (bitstrings)
            real_solver = SamplingVQE(
                sampler=self.sampler, # Usamos el SamplerV2
                optimizer=solver_instance["optimizer"],
                ansatz=ansatz
            )
            real_solver.ansatz = ansatz 

        # 4. GENERACIÓN DE EVIDENCIA VISUAL
        print("   ...[PRUEBA DE CÓMPUTO] Extrayendo circuito (Ansatz) para evidencia...")
        evidence_path = "No generado"
        try:
            ansatz_to_draw = None
            if hasattr(real_solver, 'ansatz'):
                ansatz_to_draw = real_solver.ansatz
            
            if ansatz_to_draw:
                base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../data'))
                if not os.path.exists(base_path):
                    os.makedirs(base_path, exist_ok=True)

                img_filename = "qiskit_circuit_evidence.png"
                full_path = os.path.join(base_path, img_filename)
                
                # Visualizar
                ansatz_to_draw.decompose().draw(output='mpl', filename=full_path)
                evidence_path = f"/api/static/{img_filename}"
                print(f"   ...[EVIDENCIA] Circuito guardado en: {full_path}")
            else:
                print("   ...Info: No se encontró ansatz visible.")
                
        except Exception as e:
            print(f"   ...WARN Visualización: {e}")

        # 5. EJECUCIÓN
        optimizer = MinimumEigenOptimizer(real_solver)
        print(f"   ...Ejecutando optimización (Sampling)...")
        
        # Resolvemos el QUBO
        result = optimizer.solve(qubo)
        
        # Parseo de resultado
        ruta_raw = [v.name for v in result.variables if v.as_tuple()[1] > 0.9]
        
        return {
            "backend": "Qiskit (Aer Primitives V2)",
            "algoritmo": "QAOA (via SamplingVQE)" if isinstance(solver_instance, dict) else solver_instance.__class__.__name__,
            "problema": f"TSP de {n_ciudades} nodos",
            "variables_activas": ruta_raw,
            "costo_optimo": result.fval,
            "evidencia_visual": evidence_path
        }

    def execute_job(self, algoritmo: str, params: dict) -> dict:
        print(f"⚛️  QiskitAdapter: Ejecutando Job Adaptativo ({algoritmo.upper()}).")
        
        try:
            from qiskit_algorithms import VQE
            from qiskit_algorithms.optimizers import SLSQP
            from qiskit.circuit.library import TwoLocal
        except ImportError as e:
            msg = f"Faltan dependencias de Qiskit Algorithms: {e}"
            print(f"   ...ERROR: {msg}")
            return {"error": msg}

        # 1. Extraer parámetros dinámicos
        n_ciudades = params.get("size", 3)
        depth = params.get("depth", 1)
        seed_cp = params.get("complejidad_cp", 123)

        print(f"   ...Configuración Dinámica: TSP {n_ciudades} ciudades, Profundidad {depth}.")

        # 2. Generar problema
        np.random.seed(seed_cp)
        distancias = np.random.randint(1, 100, size=(n_ciudades, n_ciudades))
        np.fill_diagonal(distancias, 0)
        distancias = (distancias + distancias.T) // 2
        
        qp = self._create_tsp_qubo(n_ciudades, distancias)
        
        solver = None
        if "QAOA" in algoritmo.upper():
            print(f"   ...[CONFIG] Seleccionado modo QAOA (construcción tardía con reps={depth})...")
            solver = {
                "type": "QAOA",
                "reps": depth,
                "sampler": self.sampler, # Pasamos sampler V2 (aunque usamos estimator en _solve_tsp)
                "optimizer": SLSQP()
            }
            
        elif "VQE" in algoritmo.upper():
            print(f"   ...Configurando VQE (reps={depth})...")
            num_qubits = n_ciudades * n_ciudades 
            ansatz = TwoLocal(num_qubits, 'ry', 'cz', reps=depth, entanglement='linear')
            solver = VQE(estimator=self.estimator, optimizer=SLSQP(), ansatz=ansatz)
            
        else:
            msg = f"Algoritmo {algoritmo} no soportado en QiskitAdapter."
            return {"error": msg}

        return self._solve_tsp(solver, qp, n_ciudades)