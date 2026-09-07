from typing import Any

from app.core.audit_logger import get_logger
from app.core.variation_point import VariationPoint


class Planner:
    """Generate an executable adaptation plan and update MAPE-K knowledge."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self._variation_point: VariationPoint | None = None

    def plan(
        self,
        llm_configuration: dict[str, bool],
        feature_model,
        air_quality_index: int,
        problem_complexity: int,
    ) -> dict[str, Any]:
        """Create and retain the variation point selected by the analyzer."""
        del air_quality_index, problem_complexity
        formal_configuration = [
            f"{feature_key} {'enabled' if is_enabled else 'disabled'}"
            for feature_key, is_enabled in llm_configuration.items()
            if feature_key != "air_quality_manager"
        ]
        self.logger.info(
            "PLAN: Updating the knowledge base with the selected variation point."
        )
        self._variation_point = VariationPoint(
            formal_configuration,
            feature_model,
            "air_quality_manager",
        )
        return self._variation_point.get_configuration()

    def get_knowledge(self) -> VariationPoint | None:
        return self._variation_point
