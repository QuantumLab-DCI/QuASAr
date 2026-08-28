from flask import jsonify
from app.core.state import state_manager
from app.services.docker_service import DockerService
from . import legacy_bp

docker_service = DockerService()

@legacy_bp.route("/links/<string:name>")
def get_links(name):
    pv = state_manager.get_pv()
    if not pv:
        return jsonify({"error": "Sistema arrancando."}), 503
    return jsonify(pv.obtenerConfiguracionNivel(name))

@legacy_bp.route("/link/<string:name>")
def get_link(name):
    pv = state_manager.get_pv()
    if not pv:
        return jsonify({"error": "Sistema arrancando."}), 503
    return jsonify(pv.obtenerEstadoCaracteristica(name))

@legacy_bp.route("/reglaAdaptacion")
def get_regla_adaptacion():
    regla = state_manager.get_regla_adaptacion()
    if regla is None:
         return jsonify({"regla_adaptacion_actual": "N/A"}), 503
    return jsonify({"contexto_de_entrada": regla})

@legacy_bp.route("/container_logs/<string:container_name>")
def get_container_logs_real(container_name):
    """
    Endpoint PUENTE:
    Frontend -> Flask -> Docker Daemon -> Container STDOUT
    """
    return jsonify(docker_service.get_container_logs(container_name))
