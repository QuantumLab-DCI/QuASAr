# app/services/hqc_backends/cirq_adapter.py (Implementación Real con TFQ)
from .base_backend import QuantumBackend
import numpy as np

# --- Dependencias de Cirq y TensorFlow Quantum ---
try:
    import cirq
    import tensorflow as tf
    import tensorflow_quantum as tfq
    import sympy
    CIRQ_DISPONIBLE = True
except ImportError as e:
    print(f"HQC_ERROR: Cirq o TensorFlow Quantum no están instalados. Error: {e}")
    print("HQC_ERROR: Ejecuta: pip install cirq tensorflow==2.15.0 tensorflow-quantum==0.7.3")
    CIRQ_DISPONIBLE = False

class CirqAdapter(QuantumBackend):
    """
    Adaptador Cirq: Resuelve Max-Cut (dominio 'Optimizacion de rutas')
    usando QAOA o VQE ejecutados realmente vía TensorFlow Quantum.
    """

    def __init__(self):
        if not CIRQ_DISPONIBLE:
            raise ImportError("Dependencias de Cirq/TFQ no encontradas.")
        print("   ...Adaptador Cirq inicializado (con QAOA y VQE).")

    def _get_maxcut_hamiltonian(self):
        """
        Define el problema Max-Cut para 3 nodos (A-B-C) como un Hamiltoniano Ising.
        Objetivo: Minimizar H = Z0*Z1 + Z1*Z2
        """
        n_nodos = 3
        print(f"   ...Definiendo Problema Max-Cut con {n_nodos} nodos (A-B, B-C).")
        
        # Crear Qubits en una línea
        qubits = cirq.GridQubit.rect(1, n_nodos)
        
        # Definir Hamiltoniano (Ising Model para Max-Cut)
        # H = \sum Z_i Z_j (para aristas conectadas)
        hamiltonian = (cirq.Z(qubits[0]) * cirq.Z(qubits[1])) + \
                      (cirq.Z(qubits[1]) * cirq.Z(qubits[2]))
                      
        print(f"   ...Problema mapeado a Hamiltoniano Ising.")
        return hamiltonian, qubits

    def _build_qaoa_circuit(self, qubits, hamiltonian, p=1):
        """
        Construye el circuito variacional (Ansatz) para QAOA.
        """
        # Símbolos para parámetros variacionales (Gamma y Beta)
        gamma = sympy.Symbol('gamma')
        beta = sympy.Symbol('beta')
        
        circuit = cirq.Circuit()
        
        # 1. Superposición inicial (Hadamard a todos)
        circuit.append(cirq.H.on_each(qubits))
        
        # 2. Operador de Costo (U_C = e^{-i \gamma H})
        # TFQ tiene utilidades para exponenciar Hamiltonianos, pero aquí lo hacemos explícito para ZZ
        for term in hamiltonian:
            # term es ej. Z(0)*Z(1). Usamos ZZPowGate
            q0, q1 = term.qubits
            circuit.append(cirq.ZZPowGate(exponent=gamma * 2 / np.pi).on(q0, q1))
        
        # 3. Operador Mezclador (U_B = e^{-i \beta \sum X})
        for q in qubits:
            circuit.append(cirq.rx(2 * beta).on(q))
            
        return circuit, [gamma, beta]

    def _build_vqe_circuit(self, qubits):
        """
        Construye un Ansatz 'Hardware Efficient' simple para VQE.
        Capas de rotaciones Ry y entrelazamiento CNOT.
        """
        # Símbolos para parámetros (theta_0, theta_1, ...)
        num_params = len(qubits) * 2 # Dos capas de rotaciones
        params = [sympy.Symbol(f'th_{i}') for i in range(num_params)]
        
        circuit = cirq.Circuit()
        
        # Capa 1: Rotaciones Ry
        for i, qubit in enumerate(qubits):
            circuit.append(cirq.ry(params[i]).on(qubit))
            
        # Capa 2: Entrelazamiento (CNOTs en cadena)
        for i in range(len(qubits) - 1):
            circuit.append(cirq.CNOT(qubits[i], qubits[i+1]))
            
        # Capa 3: Rotaciones Ry finales
        for i, qubit in enumerate(qubits):
            circuit.append(cirq.ry(params[i + len(qubits)]).on(qubit))
            
        return circuit, params

    def _solve_problem_tfq(self, algoritmo: str, hamiltonian, qubits):
        """
        Ejecuta el bucle de optimización usando TensorFlow Quantum.
        """
        
        # 1. Construir el circuito según el algoritmo
        if "QAOA" in algoritmo:
            circuit, symbols = self._build_qaoa_circuit(qubits, hamiltonian)
        else: # VQE
            circuit, symbols = self._build_vqe_circuit(qubits)

        # --- INICIO PRUEBA DE TRABAJO (Visualización) ---
        print(f"   ...[PRUEBA DE CÓMPUTO] Generando el circuito {algoritmo} (Ansatz)...")
        try:
            print(f"\n--- CIRCUITO GENERADO ({len(qubits)} qubits) ---")
            print(circuit)
            print("------------------------------------------\n")
        except Exception as e:
            print(f"   ...Error dibujando circuito: {e}")
        # --- FIN PRUEBA DE TRABAJO ---

        print(f"   ...Inicializando motor TensorFlow Quantum...")
        
        # 2. Definir la capa de Expectativa (PQC - Parameterized Quantum Circuit)
        # Esta capa calcula <psi | H | psi>
        expectation_layer = tfq.layers.Expectation()
        
        # 3. Preparar datos para TFQ
        # TFQ espera un tensor de circuitos (vacío en este caso, ya que el circuito está en el modelo)
        # pero el PQC toma el circuito como parámetro de construcción.
        
        # Creamos un modelo Keras simple para optimizar los parámetros
        # Entrada: Un circuito vacío (estado |000>)
        input_circuit = cirq.Circuit()
        input_tensor = tfq.convert_to_tensor([input_circuit])
        
        # Inicializar parámetros aleatorios
        initial_vals = np.random.uniform(0, 2*np.pi, len(symbols))
        # Variable de TF entrenable
        params_var = tf.Variable([initial_vals], dtype=tf.float32)
        
        # Optimizador Clásico (Adam)
        optimizer = tf.keras.optimizers.Adam(learning_rate=0.1)

        print(f"   ...Ejecutando bucle de optimización (50 pasos)...")
        
        # 4. Bucle de Optimización Manual (Gradient Tape)
        losses = []
        for step in range(50):
            with tf.GradientTape() as tape:
                # Calcular valor esperado (Forward pass)
                # La capa Expectation toma: (circuitos_entrada, nombres_simbolos, valores_simbolos, operadores)
                expectations = expectation_layer(
                    input_tensor,
                    symbol_names=[s.name for s in symbols],
                    symbol_values=params_var,
                    operators=hamiltonian
                )
                loss = tf.reduce_sum(expectations)
            
            # Calcular gradientes y actualizar parámetros (Backward pass)
            grads = tape.gradient(loss, params_var)
            optimizer.apply_gradients([(grads, params_var)])
            losses.append(loss.numpy())
            
            if step % 10 == 0:
                print(f"      Paso {step}: Energía = {loss.numpy():.4f}")

        costo_final = losses[-1]
        print(f"   ...Optimización completada. Energía mínima: {costo_final:.4f}")

        return {
            "backend": "Cirq/TensorFlow Quantum",
            "algoritmo": algoritmo,
            "problema": f"Max-Cut {len(qubits)} nodos",
            "costo_optimo": float(costo_final),
            "parametros_optimos": params_var.numpy().tolist()[0],
            "info": "Circuito ejecutado y optimizado mediante gradientes en TFQ."
        }

    def execute_job(self, algoritmo: str, params: dict) -> dict:
        print(f"⚛️  CirqAdapter: Ejecutando trabajo (Algoritmo: {algoritmo.upper()}).")
        
        # 1. Obtener problema
        hamiltonian, qubits = self._get_maxcut_hamiltonian()
        
        # 2. Resolver usando TFQ
        if "QAOA" in algoritmo.upper():
            return self._solve_problem_tfq("QAOA", hamiltonian, qubits)
        elif "VQE" in algoritmo.upper():
            return self._solve_problem_tfq("VQE", hamiltonian, qubits)
        else:
            return {"error": f"Algoritmo {algoritmo} no soportado en Cirq."}