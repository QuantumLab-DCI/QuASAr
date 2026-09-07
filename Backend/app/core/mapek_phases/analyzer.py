from typing import Any

from app.core.audit_logger import get_logger
from app.core.feature_model import EXCLUDES, MANDATORY, REQUIRES
from app.core.knowledge import knowledge_base
from app.services import hybrid_quantum_service, llm_agent


class Analyzer:
    """Query the LLM and validate the proposed feature configuration."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self._current_reasoning = "Awaiting analysis."

    def _find_features_in_json(self, data: dict[str, Any]) -> dict[str, bool]:
        features: dict[str, bool] = {}
        for key, value in data.items():
            normalized_key = key.replace(" ", "_").lower()
            if isinstance(value, bool):
                features[normalized_key] = value
            elif isinstance(value, dict):
                features.update(self._find_features_in_json(value))
        return features

    def _validate_configuration(self, configuration: dict[str, bool], feature_model) -> bool:
        for feature in feature_model.features:
            for child_key, relationship_type in feature.relationships:
                if (
                    relationship_type == REQUIRES
                    and configuration.get(feature.key)
                    and not configuration.get(child_key)
                ):
                    return False
                if (
                    relationship_type == EXCLUDES
                    and configuration.get(feature.key)
                    and configuration.get(child_key)
                ):
                    return False

        for feature in feature_model.features:
            parent_enabled = configuration.get(feature.key) is True
            xor_children = [
                child_key
                for child_key, relationship_type in feature.relationships
                if relationship_type == "XOR"
            ]
            or_children = [
                child_key
                for child_key, relationship_type in feature.relationships
                if relationship_type == "OR"
            ]

            if parent_enabled:
                for child_key, relationship_type in feature.relationships:
                    if relationship_type == MANDATORY and not configuration.get(child_key):
                        return False
                if xor_children and sum(bool(configuration.get(key)) for key in xor_children) != 1:
                    return False
                if or_children and not any(configuration.get(key) for key in or_children):
                    return False
            elif configuration.get(feature.key) is False:
                for child_key, relationship_type in feature.relationships:
                    if relationship_type not in {REQUIRES, EXCLUDES} and configuration.get(child_key):
                        return False
        return True

    def analyze(
        self,
        feature_model,
        runtime_context: dict[str, Any],
        case_number: int,
    ) -> dict[str, bool] | None:
        """Return a validated configuration proposed for the runtime context."""
        backend_metrics = hybrid_quantum_service.monitor_backends()
        backend_metrics["Qiskit Simulator"]["queue_time_seconds"] = runtime_context[
            "qiskit_queue_time"
        ]
        prompt_context = f"""
        REAL-TIME RUNTIME CONTEXT (stochastic simulation, scenario
        {knowledge_base.get_current_scenario_id()}):

        1. User demand profile: "{runtime_context['user_profile']}"
        2. Environmental condition: AQI = {runtime_context['air_quality_index']}
        3. Computational workload complexity = {runtime_context['problem_complexity']}
        4. Infrastructure: SLA priority = {runtime_context['sla_priority']};
           backend observations = {backend_metrics}
        """
        llm_response = llm_agent.get_llm_configuration(
            prompt_context,
            feature_model.export_rules_text(),
        )
        if not llm_response:
            self.logger.error("[CASE #%s] LLM returned an empty configuration.", case_number)
            return None

        if "reasoning" in llm_response:
            self._current_reasoning = llm_response["reasoning"]
            self.logger.info(
                "[CASE #%s] LLM reasoning: %s",
                case_number,
                self._current_reasoning,
            )

        flat_configuration = self._find_features_in_json(llm_response)
        if flat_configuration.get("hybrid_quantum_computing") is False:
            quantum_features = [
                "quantum_backend",
                "quantum_algorithm",
                "qiskit_simulator",
                "cirq_simulator",
                "qaoa",
                "vqe",
            ]
            for feature_key in quantum_features:
                if flat_configuration.get(feature_key) is True:
                    flat_configuration[feature_key] = False

        configuration_with_root = flat_configuration.copy()
        configuration_with_root["air_quality_manager"] = True
        if not self._validate_configuration(configuration_with_root, feature_model):
            self.logger.error(
                "[CASE #%s] Feature-model validation rejected the LLM configuration.",
                case_number,
            )
            return None
        return flat_configuration

    def get_reasoning(self) -> str:
        return self._current_reasoning
