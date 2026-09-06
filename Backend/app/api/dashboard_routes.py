from flask import jsonify, send_from_directory

from app.config import DATA_DIR
from app.core.knowledge import knowledge_base
from app.services.file_service import FileService

from . import dashboard_bp


@dashboard_bp.route("/state")
def get_system_state():
    """Return runtime context, configuration, artifacts, and MAPE-K trace."""
    if knowledge_base.get_adaptation_rule() is None:
        return jsonify(
            {"error": "The system is starting. Select a scenario to run adaptation."}
        ), 503

    configuration = {}
    variation_point = knowledge_base.get_variation_point()
    if variation_point:
        configuration = variation_point.get_configuration()

    return jsonify(
        {
            "context": knowledge_base.get_adaptation_rule(),
            "configuration": configuration,
            "current_scenario_id": knowledge_base.get_current_scenario_id(),
            "state_image_url": "/api/static/current_state.png",
            "model_image_url": "/api/static/feature_model.png",
            "quantum_evidence_url": FileService.get_artifact_path(),
            "is_running": knowledge_base.is_running(),
            "mapek_trace": knowledge_base.get_trace(),
        }
    )


@dashboard_bp.route("/scenarios", methods=["GET"])
def get_scenarios():
    """Return the available runtime scenarios."""
    return jsonify(FileService.read_scenarios())


@dashboard_bp.route("/logs")
def get_logs():
    """Return adaptation logs with the newest entries first."""
    return jsonify({"log_content": FileService.read_logs()})


@dashboard_bp.route("/static/<path:filename>")
def get_generated_artifact(filename):
    """Serve generated artifacts from the data directory."""
    try:
        response = send_from_directory(DATA_DIR, filename)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception:
        return jsonify({"error": "File not found."}), 404
