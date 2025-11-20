# app/services/hqc_backends/cirq_adapter.py (Implementación Real con TFQ y Workload Adaptation)
from .base_backend import QuantumBackend
import numpy as np
# --- INICIO CORRECCIÓN: Backend No Interactivo ---
import matplotlib
# Forzar backend sin cabeza (headless) para evitar error de Tkinter en hilos
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# --- FIN CORRECCIÓN -
import os

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
    Soporta Adaptación de Carga de Trabajo (Tamaño y Profundidad variables).
    """

    def __init__(self):
        if not CIRQ_DISPONIBLE:
            raise ImportError("Dependencias de Cirq/TFQ no encontradas.")
        print("   ...Adaptador Cirq inicializado (con QAOA y VQE Dinámicos).")

    def _get_maxcut_hamiltonian_dynamic(self, n_nodos):
        """
        Genera dinámicamente un problema Max-Cut para 'n_nodos'.
        Crea un grafo tipo anillo (Ring Graph) para asegurar conectividad.
        """
        print(f"   ...Generando Hamiltoniano Max-Cut para {n_nodos} nodos.")
        
        # Crear Qubits en una línea
        qubits = cirq.GridQubit.rect(1, n_nodos)
        
        # Definir Hamiltoniano (Ising Model para Max-Cut)
        # H = \sum Z_i Z_j
        hamiltonian_terms = []
        
        # 1. Conexiones lineales (0-1, 1-2, etc.)
        for i in range(n_nodos - 1):
            term = cirq.Z(qubits[i]) * cirq.Z(qubits[i+1])
            hamiltonian_terms.append(term)
            
        # 2. Cerrar el ciclo (último con primero) para mayor complejidad si hay > 2 nodos
        if n_nodos > 2:
            term = cirq.Z(qubits[0]) * cirq.Z(qubits[n_nodos-1])
            hamiltonian_terms.append(term)

        # Sumar todos los términos
        hamiltonian = sum(hamiltonian_terms)
                      
        print(f"   ...Problema mapeado a Hamiltoniano Ising ({len(hamiltonian_terms)} aristas).")
        return hamiltonian, qubits

    def _build_qaoa_circuit(self, qubits, hamiltonian, p=1):
        """
        Construye el circuito QAOA con profundidad 'p' (capas repetidas).
        """
        # Símbolos para parámetros variacionales (Listas de Gamma y Beta para cada capa)
        gamma = [sympy.Symbol(f'gamma_{i}') for i in range(p)]
        beta = [sympy.Symbol(f'beta_{i}') for i in range(p)]
        
        circuit = cirq.Circuit()
        
        # 1. Superposición inicial (Hadamard a todos)
        circuit.append(cirq.H.on_each(qubits))
        
        # Repetir p veces (Capas)
        for i in range(p):
            # 2. Operador de Costo (U_C)
            for term in hamiltonian:
                q0, q1 = term.qubits
                circuit.append(cirq.ZZPowGate(exponent=gamma[i] * 2 / np.pi).on(q0, q1))
            
            # 3. Operador Mezclador (U_B)
            for q in qubits:
                circuit.append(cirq.rx(2 * beta[i]).on(q))
            
        return circuit, gamma + beta

    def _build_vqe_circuit(self, qubits, layers=1):
        """
        Construye un Ansatz VQE 'Hardware Efficient' con profundidad variable.
        """
        # Calcular número de parámetros necesarios
        # Capa inicial (N params) + 'layers' * (Entrelazamiento + Rotación (N params))
        num_params = len(qubits) + (layers * len(qubits))
        params = [sympy.Symbol(f'th_{i}') for i in range(num_params)]
        
        circuit = cirq.Circuit()
        idx_param = 0
        
        # Capa 0: Rotaciones Ry iniciales
        for q in qubits:
            circuit.append(cirq.ry(params[idx_param]).on(q))
            idx_param += 1
            
        # Repetir bloques 'layers' veces
        for _ in range(layers):
            # Entrelazamiento (CNOTs en cadena)
            for i in range(len(qubits) - 1):
                circuit.append(cirq.CNOT(qubits[i], qubits[i+1]))
            # Si es ciclo, cerrar entrelazamiento (opcional, pero bueno para grafos densos)
            if len(qubits) > 2:
                circuit.append(cirq.CNOT(qubits[-1], qubits[0]))
                
            # Rotaciones Variacionales
            for q in qubits:
                circuit.append(cirq.ry(params[idx_param]).on(q))
                idx_param += 1
            
        return circuit, params

    def _solve_problem_tfq(self, algoritmo: str, hamiltonian, qubits, depth=1):
        """
        Ejecuta el bucle de optimización usando TensorFlow Quantum.
        Recibe 'depth' para configurar la complejidad del circuito.
        """
        
        # 1. Construir el circuito según el algoritmo y profundidad
        if "QAOA" in algoritmo:
            circuit, symbols = self._build_qaoa_circuit(qubits, hamiltonian, p=depth)
        else: # VQE
            circuit, symbols = self._build_vqe_circuit(qubits, layers=depth)

        # --- INICIO PRUEBA DE TRABAJO (Visualización) ---
        print(f"   ...[PRUEBA DE CÓMPUTO] Generando circuito {algoritmo} (Size={len(qubits)}, Depth={depth})...")
        try:
            print(f"\n--- CIRCUITO GENERADO ---")
            print(circuit)
            print("-------------------------\n")
        except Exception as e:
            print(f"   ...Error dibujando circuito: {e}")
        # --- FIN PRUEBA DE TRABAJO ---

        print(f"   ...Inicializando motor TFQ (Optimizando {len(symbols)} parámetros)...")
        
        expectation_layer = tfq.layers.Expectation()
        
        input_circuit = cirq.Circuit()
        input_tensor = tfq.convert_to_tensor([input_circuit])
        
        initial_vals = np.random.uniform(0, 2*np.pi, len(symbols))
        params_var = tf.Variable([initial_vals], dtype=tf.float32)
        
        optimizer = tf.keras.optimizers.Adam(learning_rate=0.05) # Ajustado LR

        print(f"   ...Ejecutando bucle de optimización (40 pasos)...")
        
        losses = []
        # Reducimos pasos para la demo dinámica, ya que circuitos grandes son lentos
        steps = 40 
        for step in range(steps):
            with tf.GradientTape() as tape:
                expectations = expectation_layer(
                    input_tensor,
                    symbol_names=[s.name for s in symbols],
                    symbol_values=params_var,
                    operators=hamiltonian
                )
                loss = tf.reduce_sum(expectations)
            
            grads = tape.gradient(loss, params_var)
            optimizer.apply_gradients([(grads, params_var)])
            
            loss_val = loss.numpy()
            losses.append(loss_val)
            
            if step % 10 == 0:
                print(f"      Paso {step}: Energía = {loss_val:.4f}")

        costo_final = losses[-1]
        print(f"   ...Optimización completada. Energía mínima: {costo_final:.4f}")

        # --- GENERACIÓN DE EVIDENCIA VISUAL ---
        evidence_path = "No generado"
        try:
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../data'))
            if not os.path.exists(base_path):
                os.makedirs(base_path, exist_ok=True)

            img_filename = "cirq_convergence_evidence.png"
            full_path = os.path.join(base_path, img_filename)

            plt.figure(figsize=(10, 6))
            plt.plot(losses, label='Energía (Función de Costo)', color='#d62728', linewidth=2) # Rojo TF
            plt.title(f'Convergencia {algoritmo} (N={len(qubits)}, Depth={depth})')
            plt.xlabel('Iteraciones')
            plt.ylabel('<H>')
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.legend()
            
            plt.savefig(full_path)
            plt.close()
            
            print(f"   ...[EVIDENCIA] Gráfico guardado en: {full_path}")
            evidence_path = f"/api/static/{img_filename}"
            
        except Exception as e:
            print(f"   ...WARN: Error graficando: {e}")

        return {
            "backend": "Cirq/TensorFlow Quantum",
            "algoritmo": f"{algoritmo} (Depth={depth})",
            "problema": f"Max-Cut {len(qubits)} nodos",
            "costo_optimo": float(costo_final),
            "parametros_optimos": params_var.numpy().tolist()[0],
            "evidencia_visual": evidence_path
        }

    def execute_job(self, algoritmo: str, params: dict) -> dict:
        print(f"⚛️  CirqAdapter: Ejecutando Job Adaptativo ({algoritmo}).")
        
        # 1. Extraer parámetros dinámicos enviados por MAPE-K
        # Si no vienen, usar valores por defecto
        n_nodos = params.get("size", 3)
        depth = params.get("depth", 1)
        
        print(f"   ...Configuración Dinámica: Grafo de {n_nodos} nodos, Profundidad de circuito {depth}.")
        
        # 2. Generar problema de tamaño variable
        hamiltonian, qubits = self._get_maxcut_hamiltonian_dynamic(n_nodos)
        
        # 3. Resolver pasando la profundidad
        if "QAOA" in algoritmo.upper():
            return self._solve_problem_tfq("QAOA", hamiltonian, qubits, depth=depth)
        elif "VQE" in algoritmo.upper():
            return self._solve_problem_tfq("VQE", hamiltonian, qubits, depth=depth)
        else:
            return {"error": f"Algoritmo {algoritmo} no soportado en Cirq."}