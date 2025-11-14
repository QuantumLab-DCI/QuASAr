import os
from flask import Flask
from flask_cors import CORS
from pathlib import Path

# --- Definición de Rutas ---
# Apunta a la raíz de /Backend
app_path = Path(__file__).resolve().parent.parent 

# --- Variables Globales (Estado) ---
mc_global = None
pv_global = None
regla_global = None

# --- Objeto App Global ---
# Definido globalmente para que 'routes.py' pueda importarlo
app = Flask(__name__)

def create_app():
    """
    Application Factory: Crea y configura la instancia de la app Flask.
    """
    global mc_global
    
    # Configurar CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}}) 

    # 1. Cargar el Modelo de Características (las reglas)
    from .core import grafo_mc
    mc_global = grafo_mc.generarPosiblesEstados()
    
    # 2. Registrar los endpoints de la API (importación local para evitar circularidad)
    with app.app_context():
        from . import routes
    
    return app, mc_global

def setup_startup_tasks(mc):
    """ Tareas que se ejecutan una sola vez al inicio (generación del modelo estático). """
    from .services import visualizador_grafo
    print("Generando visualización del modelo estático...")
    try:
        model_img_path = os.path.join(app_path, 'data', 'modelo_caracteristicas')
        visualizador_grafo.generar_visualizacion_modelo(
            mc, nombre_archivo=model_img_path
        )
        print(f"Visualización guardada en {model_img_path}.png")
    except Exception as e:
        print(f"[startup] Error al generar la visualización del modelo: {e}")

def setup_background_tasks(mc):
    """ Inicia el bucle MAPE-K en un hilo de fondo (definido en tasks.py). """
    from . import task
    task.setup_background_tasks(mc)