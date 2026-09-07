import datetime
import time
from typing import Any

from app.config import LOG_FILE
from app.core.audit_logger import get_logger
from app.core.knowledge import knowledge_base
from app.services import hybrid_quantum_service
from app.services.docker_service import DockerService


class Executor:
    """Apply infrastructure changes and run selected quantum workloads."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.docker_service = DockerService()
        self.log_path = LOG_FILE

    def execute(
        self,
        adaptation_plan: dict[str, bool],
        case_number: int,
        runtime_context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Apply the adaptation plan and return execution trace events."""
        trace_events: list[dict[str, Any]] = []
        if not adaptation_plan:
            return trace_events

        self.logger.info("[CASE #%s] Applying infrastructure reconfiguration.", case_number)
        with open(self.log_path, "a", encoding="utf-8") as log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"\n--- RECONFIGURATION {timestamp} ---\n")
            for container in self.docker_service.list_containers(all=True):
                desired_state = adaptation_plan.get(container.name)
                if desired_state is None:
                    continue
                try:
                    target_container = self.docker_service.get_container(container.id)
                    if target_container is None:
                        continue
                    if desired_state and target_container.status == "exited":
                        target_container.start()
                        log_file.write(f"[+] Container '{container.name}' started.\n")
                        self.logger.info(
                            "[CASE #%s] Container '%s' enabled.",
                            case_number,
                            container.name,
                        )
                    elif not desired_state and target_container.status == "running":
                        target_container.stop()
                        log_file.write(f"[-] Container '{container.name}' stopped.\n")
                        self.logger.info(
                            "[CASE #%s] Container '%s' disabled.",
                            case_number,
                            container.name,
                        )
                except Exception as error:
                    action = "enable" if desired_state else "disable"
                    self.logger.error(
                        "[CASE #%s] Could not %s container '%s': %s",
                        case_number,
                        action,
                        container.name,
                        error,
                    )

        if adaptation_plan.get("hybrid_quantum_computing") is True:
            quantum_event = self._execute_hybrid_quantum_workload(
                adaptation_plan,
                case_number,
                runtime_context,
            )
            if quantum_event:
                trace_events.append(quantum_event)
        return trace_events

    def _execute_hybrid_quantum_workload(
        self,
        adaptation_plan: dict[str, bool],
        case_number: int,
        runtime_context: dict[str, Any],
    ) -> dict[str, Any] | None:
        qaoa_enabled = adaptation_plan.get("qaoa") is True
        vqe_enabled = adaptation_plan.get("vqe") is True
        if not (qaoa_enabled or vqe_enabled):
            return None

        try:
            backend_key = next(
                (
                    key
                    for key in ["qiskit_simulator", "cirq_simulator"]
                    if adaptation_plan.get(key)
                ),
                None,
            )
            if backend_key is None:
                return None

            algorithm_id = "QAOA" if qaoa_enabled else "VQE"
            backend_name = backend_key.replace("_", " ").title()
            problem_complexity = runtime_context.get("problem_complexity", 100)
            problem_size = 3 if problem_complexity < 250 else 4
            circuit_depth = 2 if problem_complexity >= 400 else 1
            backend_adapter = hybrid_quantum_service.get_backend_adapter(backend_name)
            if backend_adapter is None:
                return None

            problem_id = (
                f"{knowledge_base.get_current_scenario_id()}_{int(time.time())}"
            )
            parameters = {
                "problem_id": problem_id,
                "problem_complexity": problem_complexity,
                "problem_size": problem_size,
                "circuit_depth": circuit_depth,
            }
            self.logger.info(
                "[CASE #%s] Starting hybrid quantum-classical job on %s (%s).",
                case_number,
                backend_name,
                algorithm_id,
            )
            result = backend_adapter.execute_job(
                algorithm_id=algorithm_id,
                parameters=parameters,
            )
            objective_value = result.get("objective_value")
            with open(self.log_path, "a", encoding="utf-8") as log_file:
                log_file.write(
                    f"Hybrid quantum-classical job objective={objective_value}\n"
                )
            return {
                "phase": "EXECUTE",
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                "message": "The hybrid quantum-classical job completed.",
                "details": {
                    "objective_value": (
                        f"{objective_value:.4f}" if objective_value is not None else None
                    ),
                    "artifact_url": result.get("artifact_url"),
                    "backend": backend_name,
                },
            }
        except Exception as error:
            self.logger.error(
                "[CASE #%s] Hybrid quantum-classical execution failed: %s",
                case_number,
                error,
            )
            return {
                "phase": "EXECUTE",
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                "message": f"Hybrid quantum-classical execution failed: {error}",
                "details": None,
            }
