# app/services/hqc_backends/cirq_adapter.py (Versión Final: SVG -> PNG con CairoSVG)
from .base_backend import QuantumBackend
import numpy as np
import os

# --- Dependencias de Cirq, TFQ y Herramientas Gráficas ---
try:
    import cirq
    import tensorflow as tf
    import tensorflow_quantum as tfq
    import sympy
    
    # Herramientas para visualización
    from cirq.contrib.svg import SVGCircuit # Genera el SVG bonito
    import cairosvg                         # Convierte SVG a PNG
    
    CIRQ_DISPONIBLE = True
except ImportError as e:
    print(f"HQC_ERROR: Faltan dependencias (cirq, tfq o cairosvg). Error: {e}")
    print("HQC_ERROR: Ejecuta: pip install cirq tensorflow==2.15.0 tensorflow-quantum==0.7.3 cairosvg")
    CIRQ_DISPONIBLE = False

class CirqAdapter(QuantumBackend):
    """
    Adaptador Cirq: Resuelve Max-Cut usando TFQ.
    Genera EVIDENCIA VISUAL DEL CIRCUITO COMO PNG (vía CairoSVG).
    """

    def __init__(self):
        if not CIRQ_DISPONIBLE:
            raise ImportError("Dependencias de Cirq/TFQ/CairoSVG no encontradas.")
        print("   ...Adaptador Cirq inicializado (Salida Visual: PNG de alta calidad).")

    def _get_maxcut_hamiltonian_dynamic(self, n_nodos):
        print(f"   ...Generando Hamiltoniano Max-Cut para {n_nodos} nodos.")
        qubits = cirq.GridQubit.rect(1, n_nodos)
        hamiltonian_terms = []
        
        for i in range(n_nodos - 1):
            term = cirq.Z(qubits[i]) * cirq.Z(qubits[i+1])
            hamiltonian_terms.append(term)
            
        if n_nodos > 2:
            term = cirq.Z(qubits[0]) * cirq.Z(qubits[n_nodos-1])
            hamiltonian_terms.append(term)

        return sum(hamiltonian_terms), qubits

    def _build_qaoa_circuit(self, qubits, hamiltonian, p=1):
        gamma = [sympy.Symbol(f'gamma_{i}') for i in range(p)]
        beta = [sympy.Symbol(f'beta_{i}') for i in range(p)]
        
        circuit = cirq.Circuit()
        circuit.append(cirq.H.on_each(qubits))
        
        for i in range(p):
            for term in hamiltonian:
                q0, q1 = term.qubits
                circuit.append(cirq.ZZPowGate(exponent=gamma[i] * 2 / np.pi).on(q0, q1))
            for q in qubits:
                circuit.append(cirq.rx(2 * beta[i]).on(q))
            
        return circuit, gamma + beta

    def _build_vqe_circuit(self, qubits, layers=1):
        num_params = len(qubits) + (layers * len(qubits))
        params = [sympy.Symbol(f'th_{i}') for i in range(num_params)]
        
        circuit = cirq.Circuit()
        idx = 0
        
        for q in qubits:
            circuit.append(cirq.ry(params[idx]).on(q))
            idx += 1
            
        for _ in range(layers):
            for i in range(len(qubits) - 1):
                circuit.append(cirq.CNOT(qubits[i], qubits[i+1]))
            if len(qubits) > 2:
                circuit.append(cirq.CNOT(qubits[-1], qubits[0]))
            for q in qubits:
                circuit.append(cirq.ry(params[idx]).on(q))
                idx += 1
            
        return circuit, params

    def _solve_problem_tfq(self, algoritmo: str, hamiltonian, qubits, depth=1):
        
        # 1. Construir circuito
        if "QAOA" in algoritmo:
            circuit, symbols = self._build_qaoa_circuit(qubits, hamiltonian, p=depth)
        else: 
            circuit, symbols = self._build_vqe_circuit(qubits, layers=depth)

        # --- GENERACIÓN DE EVIDENCIA VISUAL (SVG -> PNG) ---
        print(f"   ...[PRUEBA DE CÓMPUTO] Generando diagrama PNG del circuito {algoritmo}...")
        evidence_path = "No generado"
        try:
            # Ruta base: Backend/data
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../data'))
            
            if not os.path.exists(base_path):
                os.makedirs(base_path, exist_ok=True)

            # Nombres de archivo
            svg_filename = "cirq_circuit_evidence.svg"
            png_filename = "cirq_circuit_evidence.png"
            
            full_path_svg = os.path.join(base_path, svg_filename)
            full_path_png = os.path.join(base_path, png_filename)

            # 1. Generar contenido SVG con Cirq
            svg_content = SVGCircuit(circuit)._repr_svg_()

            # Guardar SVG temporalmente (útil para debug)
            with open(full_path_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

            # 2. Convertir a PNG usando CairoSVG
            # scale=2.0 mejora la resolución de la imagen resultante
            cairosvg.svg2png(url=full_path_svg, write_to=full_path_png, scale=2.0)

            print(f"   ...[EVIDENCIA] Diagrama PNG guardado en: {full_path_png}")
            evidence_path = f"/api/static/{png_filename}"
            
        except Exception as e:
            print(f"   ...WARN Visualización PNG: {e}")
            print(circuit) # Fallback a texto en consola
        # --------------------------------------

        # 2. Ejecución (Optimización)
        print(f"   ...Inicializando motor TFQ...")
        expectation_layer = tfq.layers.Expectation()
        
        input_circuit = cirq.Circuit()
        input_tensor = tfq.convert_to_tensor([input_circuit])
        
        initial_vals = np.random.uniform(0, 2*np.pi, len(symbols))
        params_var = tf.Variable([initial_vals], dtype=tf.float32)
        
        optimizer = tf.keras.optimizers.Adam(learning_rate=0.05)

        print(f"   ...Ejecutando optimización (30 pasos)...")
        losses = []
        for step in range(30):
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
            losses.append(loss.numpy())

        costo_final = losses[-1]
        print(f"   ...Optimización completada. Energía mínima: {costo_final:.4f}")

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
        
        n_nodos = params.get("size", 3)
        depth = params.get("depth", 1)
        
        print(f"   ...Configuración: Grafo {n_nodos} nodos, Profundidad {depth}.")
        hamiltonian, qubits = self._get_maxcut_hamiltonian_dynamic(n_nodos)
        
        if "QAOA" in algoritmo.upper():
            return self._solve_problem_tfq("QAOA", hamiltonian, qubits, depth=depth)
        elif "VQE" in algoritmo.upper():
            return self._solve_problem_tfq("VQE", hamiltonian, qubits, depth=depth)
        else:
            return {"error": f"Algoritmo {algoritmo} no soportado."}