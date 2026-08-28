from flask import Flask
from flask_cors import CORS
from app.core.state import state_manager
from app.config import MODEL_IMAGE_DIR
import os

def create_app():
    """
    Application Factory: Crea y configura la instancia de la app Flask.
    """
    # --- Objeto App Global ---
    app = Flask(__name__)
    
    # Configurar CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}}) 
    
    # 1. Cargar el Modelo de Características
    from .core import grafo_mc
    mc = grafo_mc.generarPosiblesEstados()
    
    # 2. Inicializar el State Manager
    state_manager.set_mc(mc)
    
    # 3. Registrar los blueprints
    from .api import dashboard_bp, control_bp, legacy_bp
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(control_bp, url_prefix='/api')
    app.register_blueprint(legacy_bp, url_prefix='/api')
    
    return app, mc

def setup_startup_tasks(mc):
    """ Tareas de inicio (Solo genera la imagen estática del modelo). """
    from .services import visualizador_grafo
    print("Generando visualización del modelo estático...")
    try:
        visualizador_grafo.generar_visualizacion_modelo(
            mc, nombre_archivo=MODEL_IMAGE_DIR
        )
        print(f"Visualización guardada en {MODEL_IMAGE_DIR}.png")
    except Exception as e:
        print(f"[startup] Error al generar la visualización del modelo: {e}")