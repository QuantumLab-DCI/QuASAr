from threading import Lock
from typing import Any


class KnowledgeBase:
    """Process-local knowledge shared across MAPE-K cycles and API requests."""

    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self.feature_model = None
        self.variation_point = None
        self.adaptation_rule = None
        self.trace: list[dict[str, Any]] = []
        self.current_scenario_id = 1
        self._is_running = False
        self.execution_counter = 0

    def get_feature_model(self):
        return self.feature_model

    def set_feature_model(self, feature_model) -> None:
        self.feature_model = feature_model

    def get_variation_point(self):
        return self.variation_point

    def set_variation_point(self, variation_point) -> None:
        self.variation_point = variation_point

    def get_adaptation_rule(self):
        return self.adaptation_rule

    def set_adaptation_rule(self, adaptation_rule) -> None:
        self.adaptation_rule = adaptation_rule

    def get_trace(self) -> list[dict[str, Any]]:
        return self.trace

    def set_trace(self, trace: list[dict[str, Any]]) -> None:
        self.trace = trace

    def get_current_scenario_id(self) -> int:
        return self.current_scenario_id

    def set_current_scenario_id(self, scenario_id: int) -> None:
        self.current_scenario_id = scenario_id

    def is_running(self) -> bool:
        return self._is_running

    def set_running(self, is_running: bool) -> None:
        self._is_running = is_running

    def increment_execution_counter(self) -> int:
        self.execution_counter += 1
        return self.execution_counter

    def get_execution_counter(self) -> int:
        return self.execution_counter


knowledge_base = KnowledgeBase()
