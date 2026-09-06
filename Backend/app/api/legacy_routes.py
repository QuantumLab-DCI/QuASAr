"""Expose compatibility endpoints for legacy clients."""

from flask import jsonify

from app.core.knowledge import knowledge_base
from app.services.docker_service import DockerService

from . import legacy_bp


docker_service = DockerService()


@legacy_bp.route("/links/<string:name>")
def get_links(name):
    """Return enabled child links for a feature."""
    variation_point = knowledge_base.get_variation_point()
    if not variation_point:
        return jsonify({"error": "The system is starting."}), 503
    return jsonify(variation_point.get_level_configuration(name))


@legacy_bp.route("/link/<string:name>")
def get_link(name):
    """Return link metadata for an enabled feature."""
    variation_point = knowledge_base.get_variation_point()
    if not variation_point:
        return jsonify({"error": "The system is starting."}), 503
    return jsonify(variation_point.get_feature_state(name))


@legacy_bp.route("/adaptation-rule")
def get_adaptation_rule():
    """Return the latest adaptation context."""
    adaptation_rule = knowledge_base.get_adaptation_rule()
    if adaptation_rule is None:
        return jsonify({"adaptation_rule": None}), 503
    return jsonify({"context": adaptation_rule})


@legacy_bp.route("/container_logs/<string:container_name>")
def get_container_logs(container_name):
    """Return container output through the Flask-to-Docker API bridge."""
    return jsonify(docker_service.get_container_logs(container_name))
