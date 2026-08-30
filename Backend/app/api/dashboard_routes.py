from flask import jsonify, send_from_directory
from app.core.state import state_manager
from app.config import DATA_DIR
from app.services.file_service import FileService
from . import dashboard_bp
import os

@dashboard_bp.route("/estado")
def get_estado_general():
    """ 
    Main dashboard endpoint.
    Return the context, active configuration, visual evidence, and
    DETAILED TRACE of the MAPE-K cycle.
    """
    if state_manager.get_regla_adaptacion() is None:
         return jsonify({"error": "El sistema está arrancando. Seleccione un escenario."}), 503
    
    evidencia_cuantica = FileService.get_evidence_path()
    
    # Get the actual configuration
    config_real = {}
    pv = state_manager.get_pv()
    if pv:
        config_real = pv.obtenerConfiguracion()

    return jsonify({
        "contexto": state_manager.get_regla_adaptacion(),
        "configuracion": config_real,
        "escenario_actual_id": state_manager.get_escenario_id(), 
        "imagen_estado_url": "/api/static/estado_actual.png", 
        "imagen_modelo_url": "/api/static/modelo_caracteristicas.png",
        "evidencia_cuantica_url": evidencia_cuantica,
        "en_ejecucion": state_manager.is_running(),
        "mapek_trace": state_manager.get_trace()
    })

@dashboard_bp.route("/escenarios", methods=['GET'])
def get_escenarios():
    """ Return the list of scenarios from the JSON file. """
    scenarios = FileService.read_scenarios()
    return jsonify(scenarios)

@dashboard_bp.route("/logs")
def get_logs():
    return jsonify({"log_content": FileService.read_logs()})

@dashboard_bp.route("/static/<path:filename>")
def static_files(filename):
    """ Serve generated files (images) from the /data directory. """
    try:
        response = send_from_directory(DATA_DIR, filename)
        # Disable caching for dynamic images
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception:
        return jsonify({"error": "Archivo no encontrado"}), 404
