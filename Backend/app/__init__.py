from flask import Flask
from flask_cors import CORS

from app.config import MODEL_IMAGE_DIR
from app.core.knowledge import knowledge_base

def create_app():
    """Create the Flask application and its feature model."""
    app = Flask(__name__)
    
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    from .core.feature_model import build_air_quality_feature_model
    feature_model = build_air_quality_feature_model()
    
    knowledge_base.set_feature_model(feature_model)
    
    from .api import dashboard_bp, control_bp, legacy_bp
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(control_bp, url_prefix="/api")
    app.register_blueprint(legacy_bp, url_prefix="/api")
    
    return app, feature_model

def setup_startup_tasks(feature_model):
    """Generate the static feature-model image during application startup."""
    from .services import graph_visualizer
    print("Generating the static feature-model visualization.")
    try:
        graph_visualizer.generate_feature_model_visualization(
            feature_model, filename=MODEL_IMAGE_DIR
        )
        print(f"Feature-model visualization saved to {MODEL_IMAGE_DIR}.png.")
    except Exception as e:
        print(f"[startup] Could not generate the feature-model visualization: {e}")
