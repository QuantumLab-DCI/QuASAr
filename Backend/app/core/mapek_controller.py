import datetime
from typing import Any

from app.core.audit_logger import get_logger
from app.core.mapek_phases.analyzer import Analyzer
from app.core.mapek_phases.executor import Executor
from app.core.mapek_phases.monitor import Monitor
from app.core.mapek_phases.planner import Planner


class MAPEKController:
    """Orchestrate the Monitor, Analyze, Plan, and Execute phases."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self._mapek_trace: list[dict[str, Any]] = []
        self._current_case = 0
        self.monitor_phase = Monitor()
        self.analyzer_phase = Analyzer()
        self.planner_phase = Planner()
        self.executor_phase = Executor()
        self._last_context: dict[str, Any] = {}

    def _record_trace_event(
        self,
        phase: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        event = {
            "phase": phase,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "message": message,
            "details": details,
        }
        self._mapek_trace.append(event)
        print(f"[{phase}] {message}")

    def run_adaptation_cycle(
        self,
        feature_model,
        target_id: int,
        case_number: int = 0,
    ) -> None:
        """Run one complete MAPE-K adaptation cycle for a scenario."""
        self._current_case = case_number
        self._mapek_trace = []

        runtime_context = self.monitor_phase.monitor(target_id, case_number)
        self._last_context = runtime_context
        self._record_trace_event(
            "MONITOR",
            f"Runtime context collected for scenario {target_id}.",
            {
                "air_quality_index": runtime_context["air_quality_index"],
                "problem_complexity": runtime_context["problem_complexity"],
                "qiskit_queue_time": runtime_context["qiskit_queue_time"],
                "user_profile": runtime_context["user_profile"],
            },
        )

        self._record_trace_event(
            "ANALYZE",
            "An adaptation need was identified; the intelligent agent is evaluating the feature model.",
            {
                "trigger": "runtime context change",
                "strategy": "Gemini-assisted configuration analysis",
            },
        )
        flat_configuration = self.analyzer_phase.analyze(
            feature_model,
            runtime_context,
            case_number,
        )
        if not flat_configuration:
            self._record_trace_event(
                "ANALYZE",
                "The LLM agent failed or feature-model validation rejected the configuration.",
            )
            return

        self._record_trace_event(
            "ANALYZE",
            "The intelligent agent selected a valid configuration.",
            {"reasoning": self.analyzer_phase.get_reasoning()},
        )

        executable_configuration = self.planner_phase.plan(
            flat_configuration,
            feature_model,
            runtime_context["air_quality_index"],
            runtime_context["problem_complexity"],
        )
        enabled_features = [
            key for key, is_enabled in executable_configuration.items() if is_enabled
        ]
        self._record_trace_event(
            "PLAN",
            "The adaptation plan was generated and recorded in the knowledge base.",
            {
                "strategy": "runtime container and backend reconfiguration",
                "enabled_features": enabled_features,
            },
        )

        self._record_trace_event(
            "EXECUTE",
            "Applying the adaptation plan to the hybrid quantum-classical infrastructure.",
            {"mechanism": "Docker API and hybrid quantum service"},
        )
        execution_trace = self.executor_phase.execute(
            executable_configuration,
            case_number,
            runtime_context,
        )
        self._mapek_trace.extend(execution_trace)
        self._record_trace_event(
            "EXECUTE",
            "The MAPE-K adaptation cycle completed successfully.",
        )

    def get_knowledge(self):
        return self.planner_phase.get_knowledge()

    def get_adaptation_rule(self) -> dict[str, Any]:
        return {
            "air_quality_index": self._last_context.get("air_quality_index"),
            "problem_complexity": self._last_context.get("problem_complexity"),
            "sla_priority": self._last_context.get("sla_priority"),
            "qiskit_queue_time": self._last_context.get("qiskit_queue_time"),
            "user_profile": self._last_context.get("user_profile"),
            "scenario_name": self._last_context.get("scenario_name"),
            "reasoning": self.analyzer_phase.get_reasoning(),
        }

    def get_trace(self) -> list[dict[str, Any]]:
        return self._mapek_trace
