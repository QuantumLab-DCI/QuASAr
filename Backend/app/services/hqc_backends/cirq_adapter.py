import os

import numpy as np

from .base_backend import QuantumBackend


try:
    import cairosvg
    import cirq
    import sympy
    import tensorflow as tf
    import tensorflow_quantum as tfq
    from cirq.contrib.svg import SVGCircuit

    CIRQ_AVAILABLE = True
except ImportError as error:
    print(f"HQC_ERROR: Required Cirq, TFQ, or CairoSVG dependency is unavailable: {error}")
    CIRQ_AVAILABLE = False


class CirqAdapter(QuantumBackend):
    """Solve adaptive Max-Cut workloads with Cirq and TensorFlow Quantum."""

    def __init__(self) -> None:
        if not CIRQ_AVAILABLE:
            raise ImportError("Required Cirq, TFQ, or CairoSVG dependencies are unavailable.")
        print("Cirq adapter initialized with PNG artifact output.")

    def _get_maxcut_hamiltonian(self, node_count: int):
        print(f"Generating a Max-Cut Hamiltonian for {node_count} nodes.")
        qubits = cirq.GridQubit.rect(1, node_count)
        terms = [
            cirq.Z(qubits[index]) * cirq.Z(qubits[index + 1])
            for index in range(node_count - 1)
        ]
        if node_count > 2:
            terms.append(cirq.Z(qubits[0]) * cirq.Z(qubits[node_count - 1]))
        return sum(terms), qubits

    def _build_qaoa_circuit(self, qubits, hamiltonian, depth: int = 1):
        gamma = [sympy.Symbol(f"gamma_{index}") for index in range(depth)]
        beta = [sympy.Symbol(f"beta_{index}") for index in range(depth)]
        circuit = cirq.Circuit(cirq.H.on_each(qubits))
        for layer_index in range(depth):
            for term in hamiltonian:
                first_qubit, second_qubit = term.qubits
                circuit.append(
                    cirq.ZZPowGate(exponent=gamma[layer_index] * 2 / np.pi).on(
                        first_qubit,
                        second_qubit,
                    )
                )
            for qubit in qubits:
                circuit.append(cirq.rx(2 * beta[layer_index]).on(qubit))
        return circuit, gamma + beta

    def _build_vqe_circuit(self, qubits, depth: int = 1):
        parameter_count = len(qubits) + depth * len(qubits)
        parameters = [sympy.Symbol(f"theta_{index}") for index in range(parameter_count)]
        circuit = cirq.Circuit()
        parameter_index = 0
        for qubit in qubits:
            circuit.append(cirq.ry(parameters[parameter_index]).on(qubit))
            parameter_index += 1
        for _layer in range(depth):
            for index in range(len(qubits) - 1):
                circuit.append(cirq.CNOT(qubits[index], qubits[index + 1]))
            if len(qubits) > 2:
                circuit.append(cirq.CNOT(qubits[-1], qubits[0]))
            for qubit in qubits:
                circuit.append(cirq.ry(parameters[parameter_index]).on(qubit))
                parameter_index += 1
        return circuit, parameters

    def _solve_problem(
        self,
        algorithm_id: str,
        hamiltonian,
        qubits,
        depth: int,
        problem_id: str,
        problem_complexity: int,
    ) -> dict:
        if "QAOA" in algorithm_id:
            circuit, symbols = self._build_qaoa_circuit(qubits, hamiltonian, depth)
        else:
            circuit, symbols = self._build_vqe_circuit(qubits, depth)

        artifact_url = None
        try:
            data_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../../data")
            )
            os.makedirs(data_path, exist_ok=True)
            svg_filename = "cirq_circuit_artifact.svg"
            png_filename = "cirq_circuit_artifact.png"
            svg_path = os.path.join(data_path, svg_filename)
            png_path = os.path.join(data_path, png_filename)
            with open(svg_path, "w", encoding="utf-8") as svg_file:
                svg_file.write(SVGCircuit(circuit)._repr_svg_())
            cairosvg.svg2png(url=svg_path, write_to=png_path, scale=2.0)
            artifact_url = f"/api/static/{png_filename}"
            print(f"Cirq circuit artifact saved to {png_path}.")
        except Exception as error:
            print(f"HQC_WARNING: Could not generate the Cirq circuit artifact: {error}")
            print(circuit)

        expectation_layer = tfq.layers.Expectation()
        input_tensor = tfq.convert_to_tensor([cirq.Circuit()])
        initial_values = np.random.uniform(0, 2 * np.pi, len(symbols))
        parameter_variable = tf.Variable([initial_values], dtype=tf.float32)
        optimizer = tf.keras.optimizers.Adam(learning_rate=0.05)
        losses = []
        for _step in range(30):
            with tf.GradientTape() as tape:
                expectations = expectation_layer(
                    input_tensor,
                    symbol_names=[symbol.name for symbol in symbols],
                    symbol_values=parameter_variable,
                    operators=hamiltonian,
                )
                loss = tf.reduce_sum(expectations)
            gradients = tape.gradient(loss, parameter_variable)
            optimizer.apply_gradients([(gradients, parameter_variable)])
            losses.append(loss.numpy())

        objective_value = float(losses[-1])
        print(f"Optimization completed with objective value {objective_value:.4f}.")
        return {
            "backend": "Cirq/TensorFlow Quantum",
            "algorithm_id": f"{algorithm_id} (depth={depth})",
            "problem_id": problem_id,
            "problem_complexity": problem_complexity,
            "objective_value": objective_value,
            "optimized_parameters": parameter_variable.numpy().tolist()[0],
            "artifact_url": artifact_url,
        }

    def execute_job(self, algorithm_id: str, parameters: dict) -> dict:
        """Execute a supported QAOA or VQE workload."""
        print(f"CirqAdapter: Executing adaptive {algorithm_id} job.")
        node_count = parameters.get("problem_size", 3)
        depth = parameters.get("circuit_depth", 1)
        hamiltonian, qubits = self._get_maxcut_hamiltonian(node_count)
        if algorithm_id.upper() not in {"QAOA", "VQE"}:
            return {"error": f"Algorithm {algorithm_id} is not supported."}
        return self._solve_problem(
            algorithm_id.upper(),
            hamiltonian,
            qubits,
            depth,
            parameters.get("problem_id", f"maxcut_{node_count}_nodes"),
            parameters.get("problem_complexity", 0),
        )
