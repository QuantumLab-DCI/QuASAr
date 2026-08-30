import threading

from flask import jsonify, request

from app.adaptation_task import run_on_demand_adaptation_cycle
from app.core.knowledge import knowledge_base

from . import control_bp


@control_bp.route("/select-scenario", methods=["POST"])
def select_scenario():
    """Select a scenario and start an on-demand MAPE-K cycle."""
    payload = request.json or {}
    scenario_id = payload.get("scenario_id")
    if knowledge_base.is_running():
        return jsonify(
            {"error": "The system is busy. Wait for the current cycle to finish."}
        ), 423

    if scenario_id is None:
        return jsonify({"error": "scenario_id is required."}), 400

    try:
        selected_scenario_id = int(scenario_id)
        knowledge_base.set_current_scenario_id(selected_scenario_id)
        print(f"User selected scenario {selected_scenario_id}.")
        knowledge_base.set_running(True)
        thread = threading.Thread(
            target=run_on_demand_adaptation_cycle,
            args=(knowledge_base.get_feature_model(), selected_scenario_id),
        )
        thread.start()
        return jsonify(
            {
                "status": "ok",
                "message": (
                    f"Scenario {selected_scenario_id} selected; the adaptation "
                    "cycle is running."
                ),
                "scenario_id": selected_scenario_id,
            }
        )
    except ValueError:
        return jsonify({"error": "scenario_id must be an integer."}), 400
    except Exception as error:
        print(f"Could not start the adaptation thread: {error}")
        knowledge_base.set_running(False)
        return jsonify({"error": str(error)}), 500
