import os
from flask import Flask
from flask_cors import CORS
from pathlib import Path

# --- Definición de Rutas ---
app_path = Path(__file__).resolve().parent.parent 

# --- Variables Globales (Estado) ---
mc_global = None
pv_global = None
regla_global = None
trace_global = [] # <--- ¡NUEVO! Aquí se guardará el historial del ciclo MAPE-K

# --- Variable de Control Interactivo ---
escenario_activo_id = 1 

# --- Semáforo de Estado ---
# Indica si el sistema está procesando una solicitud MAPE-K actualmente
en_ejecucion = False 
# ---------------------------------

# --- Objeto App Global ---
app = Flask(__name__)

def create_app():
    """
    Application Factory: Crea y configura la instancia de la app Flask.
    """
    global mc_global
    
    # Configurar CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}}) 

    # 1. Cargar el Modelo de Características
    from .core import grafo_mc
    mc_global = grafo_mc.generarPosiblesEstados()
    
    # 2. Registrar los endpoints
    with app.app_context():
        from . import routes
    
    return app, mc_global

def setup_startup_tasks(mc):
    """ Tareas de inicio (Solo genera la imagen estática del modelo). """
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

# --- NOTA: Se eliminó setup_background_tasks porque ahora usamos ejecución por eventos ---