import json
import os
import random
from typing import Any

from app.config import SCENARIOS_JSON
from app.core.audit_logger import get_logger


class Monitor:
    """Collect simulated environment, workload, and user-profile observations."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.scenarios = self._load_scenarios()

    def _load_scenarios(self) -> list[dict[str, Any]]:
        scenarios: list[dict[str, Any]] = []
        try:
            if os.path.exists(SCENARIOS_JSON):
                with open(SCENARIOS_JSON, "r", encoding="utf-8") as scenario_file:
                    scenarios = json.load(scenario_file)
                self.logger.info("MONITOR: Loaded %s scenarios.", len(scenarios))
        except Exception as error:
            self.logger.error("MONITOR: Could not load scenarios.json: %s", error)
        return scenarios

    def monitor(self, target_id: int, case_number: int) -> dict[str, Any]:
        """Simulate observations for the selected runtime scenario."""
        current_scenario = next(
            (scenario for scenario in self.scenarios if scenario["id"] == target_id),
            None,
        )
        scenario_name = current_scenario["name"] if current_scenario else "Unknown baseline"

        if current_scenario:
            aqi_range = current_scenario.get("air_quality_index_range", [0, 50])
            complexity_range = current_scenario.get(
                "problem_complexity_range",
                [0, 100],
            )
            queue_range = current_scenario.get("qiskit_queue_time_range", [0, 10])
            air_quality_index = random.randint(*aqi_range)
            problem_complexity = random.randint(*complexity_range)
            qiskit_queue_time = random.randint(*queue_range)
            sla_priority = current_scenario.get("sla_priority", "LATENCY")
            user_profile = random.choice(
                [
                    "Standard tourist (route services only)",
                    "Sports group (requires sports services)",
                    "Older adult (requires senior entertainment)",
                    "Family with children (requires family entertainment)",
                    "Nighttime event (requires adult entertainment)",
                ]
            )
        else:
            self.logger.warning(
                "Scenario %s was not found; baseline values will be used.",
                target_id,
            )
            air_quality_index = 50
            problem_complexity = 10
            sla_priority = "LATENCY"
            qiskit_queue_time = 5
            user_profile = "Standard"

        self.logger.info(
            "[CASE #%s] RUNTIME CONTEXT: scenario='%s' | AQI=%s | "
            "complexity=%s | QiskitQueue=%ss | user='%s'",
            case_number,
            scenario_name,
            air_quality_index,
            problem_complexity,
            qiskit_queue_time,
            user_profile,
        )
        return {
            "air_quality_index": air_quality_index,
            "problem_complexity": problem_complexity,
            "sla_priority": sla_priority,
            "qiskit_queue_time": qiskit_queue_time,
            "user_profile": user_profile,
            "scenario_name": scenario_name,
        }
