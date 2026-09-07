"""Define API blueprints and register their routes."""

from flask import Blueprint

dashboard_bp = Blueprint('dashboard', __name__)
control_bp = Blueprint('control', __name__)
legacy_bp = Blueprint('legacy', __name__)

from . import dashboard_routes, control_routes, legacy_routes
