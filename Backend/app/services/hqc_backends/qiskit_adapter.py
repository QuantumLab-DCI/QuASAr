import os

import matplotlib
import numpy as np

from .base_backend import QuantumBackend


matplotlib.use("Agg")

try:
    from qiskit_algorithms.utils import algorithm_globals

    QISKIT_AVAILABLE = True
except ImportError:
    print("HQC_WARNING: qiskit-algorithms is unavailable or incompatible.")
    QISKIT_AVAILABLE = False


class QiskitAdapter(QuantumBackend):
    """Execute adaptive route optimization with Qiskit V2 primitives."""

    def __init__(self) -> None:
        if not QISKIT_AVAILABLE:
            raise ImportError("Required Qiskit dependencies are unavailable or incompatible.")
        try:
            from qiskit_aer.primitives import EstimatorV2, SamplerV2

            self.sampler = SamplerV2()
            self.estimator = EstimatorV2()
            algorithm_globals.random_seed = 123
            print("Qiskit adapter initialized with Aer V2 primitives.")
        except ImportError:
            print("HQC_WARNING: V2 primitives unavailable; attempting V1 primitives.")
            from qiskit_aer.primitives import Estimator, Sampler

            self.sampler = Sampler()
            self.estimator = Estimator()
        except Exception as error:
            raise ImportError(f"Qiskit Aer initialization failed: {error}") from error

    def _create_tsp_qubo(self, city_count: int, distance_matrix):
        """Create a quadratic program for the traveling salesperson problem."""
        from qiskit_optimization import QuadraticProgram

        quadratic_program = QuadraticProgram()
        for city_index in range(city_count):
            for position_index in range(city_count):
                quadratic_program.binary_var(name=f"x_{city_index}_{position_index}")

        quadratic: dict[tuple[str, str], int] = {}
        for origin in range(city_count):
            for destination in range(city_count):
                if origin == destination:
                    continue
                distance = distance_matrix[origin][destination]
                for position in range(city_count):
                    next_position = (position + 1) % city_count
                    quadratic[
                        (f"x_{origin}_{position}", f"x_{destination}_{next_position}")
                    ] = distance
        quadratic_program.minimize(linear={}, quadratic=quadratic)
        for city_index in range(city_count):
            quadratic_program.linear_constraint(
                linear={f"x_{city_index}_{position}": 1 for position in range(city_count)},
                sense="==",
                rhs=1,
                name=f"city_{city_index}",
            )
        for position in range(city_count):
            quadratic_program.linear_constraint(
                linear={f"x_{city_index}_{position}": 1 for city_index in range(city_count)},
                sense="==",
                rhs=1,
                name=f"position_{position}",
            )
        return quadratic_program

    def _solve_tsp(self, solver_configuration, quadratic_program, city_count: int) -> dict:
        """Convert the problem to QUBO, solve it, and return metadata."""
        from qiskit import transpile
        from qiskit.circuit.library import QAOAAnsatz
        from qiskit_algorithms import SamplingVQE
        from qiskit_optimization.algorithms import MinimumEigenOptimizer
        from qiskit_optimization.converters import QuadraticProgramToQubo

        print("Mapping the TSP quadratic program to QUBO form.")
        qubo = QuadraticProgramToQubo().convert(quadratic_program)
        operator, _offset = qubo.to_ising()
        print(f"Generated an Ising operator with {operator.num_qubits} qubits.")
        solver = solver_configuration
        if isinstance(solver_configuration, dict) and solver_configuration.get("type") == "QAOA":
            raw_ansatz = QAOAAnsatz(
                cost_operator=operator,
                reps=solver_configuration["repetitions"],
                name="QAOA",
            )
            ansatz = transpile(raw_ansatz, basis_gates=["rx", "ry", "rz", "cx", "h"])
            solver = SamplingVQE(
                sampler=self.sampler,
                optimizer=solver_configuration["optimizer"],
                ansatz=ansatz,
            )
            solver.ansatz = ansatz

        artifact_url = None
        try:
            ansatz_to_draw = getattr(solver, "ansatz", None)
            if ansatz_to_draw:
                data_path = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "../../../data")
                )
                os.makedirs(data_path, exist_ok=True)
                artifact_filename = "qiskit_circuit_artifact.png"
                artifact_path = os.path.join(data_path, artifact_filename)
                ansatz_to_draw.decompose().draw(output="mpl", filename=artifact_path)
                artifact_url = f"/api/static/{artifact_filename}"
                print(f"Qiskit circuit artifact saved to {artifact_path}.")
        except Exception as error:
            print(f"HQC_WARNING: Could not generate the Qiskit circuit artifact: {error}")

        result = MinimumEigenOptimizer(solver).solve(qubo)
        selected_variables = [
            variable.name
            for variable in result.variables
            if variable.as_tuple()[1] > 0.9
        ]
        return {
            "backend": "Qiskit Aer Primitives V2",
            "algorithm_id": (
                "QAOA via SamplingVQE"
                if isinstance(solver_configuration, dict)
                else solver_configuration.__class__.__name__
            ),
            "problem_id": f"tsp_{city_count}_cities",
            "selected_variables": selected_variables,
            "objective_value": result.fval,
            "artifact_url": artifact_url,
        }

    def execute_job(self, algorithm_id: str, parameters: dict) -> dict:
        """Execute a QAOA or VQE route-optimization workload."""
        print(f"QiskitAdapter: Executing adaptive {algorithm_id.upper()} job.")
        try:
            from qiskit.circuit.library import TwoLocal
            from qiskit_algorithms import SamplingVQE
            from qiskit_algorithms.optimizers import SLSQP
        except ImportError as error:
            message = f"Required Qiskit Algorithms dependencies are unavailable: {error}"
            print(f"HQC_ERROR: {message}")
            return {"error": message}

        city_count = parameters.get("problem_size", 3)
        circuit_depth = parameters.get("circuit_depth", 1)
        problem_complexity = parameters.get("problem_complexity", 123)
        print(
            f"Dynamic configuration: TSP with {city_count} cities and "
            f"circuit depth {circuit_depth}."
        )
        np.random.seed(problem_complexity)
        distances = np.random.randint(1, 100, size=(city_count, city_count))
        np.fill_diagonal(distances, 0)
        distances = (distances + distances.T) // 2
        quadratic_program = self._create_tsp_qubo(city_count, distances)

        if "QAOA" in algorithm_id.upper():
            solver = {
                "type": "QAOA",
                "repetitions": circuit_depth,
                "optimizer": SLSQP(),
            }
        elif "VQE" in algorithm_id.upper():
            qubit_count = city_count * city_count
            ansatz = TwoLocal(
                qubit_count,
                "ry",
                "cz",
                reps=circuit_depth,
                entanglement="linear",
            ).decompose()
            solver = SamplingVQE(
                sampler=self.sampler,
                optimizer=SLSQP(),
                ansatz=ansatz,
            )
        else:
            return {"error": f"Algorithm {algorithm_id} is not supported by QiskitAdapter."}

        result = self._solve_tsp(solver, quadratic_program, city_count)
        result["problem_id"] = parameters.get("problem_id", result["problem_id"])
        result["problem_complexity"] = problem_complexity
        return result
