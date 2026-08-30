from flask import Flask
from flask_cors import CORS
from app.core.state import state_manager
from app.config import MODEL_IMAGE_DIR
import os

def create_app():
    """
    Application factory: create and configure the Flask application instance.
    """
    # --- Global Application Object ---
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}}) 
    
    # 1. Load the Feature Model
    from .core import grafo_mc
    mc = grafo_mc.generarPosiblesEstados()
    
    # 2. Initialize the State Manager
    state_manager.set_mc(mc)
    
    # 3. Register the blueprints
    from .api import dashboard_bp, control_bp, legacy_bp
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(control_bp, url_prefix='/api')
    app.register_blueprint(legacy_bp, url_prefix='/api')
    
    return app, mc

def setup_startup_tasks(mc):
    """ Run startup tasks (only generates the static model image). """
    from .services import visualizador_grafo
    print("Generando visualización del modelo estático...")
    try:
        visualizador_grafo.generar_visualizacion_modelo(
            mc, nombre_archivo=MODEL_IMAGE_DIR
        )
        print(f"Visualización guardada en {MODEL_IMAGE_DIR}.png")
    except Exception as e:
        print(f"[startup] Error al generar la visualización del modelo: {e}")
