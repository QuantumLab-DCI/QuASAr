import os
import time
import threading
import grafo_mc
import punto_variacion
import visualizador_grafo
from mapek import Mapek
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path

# --- Configuración de la App ---
app = Flask(__name__)
# Obtener la ruta absoluta del directorio del script
PROJECT_ROOT = Path(__file__).resolve().parent
os.chdir(PROJECT_ROOT) # Asegurarse de que estamos en el directorio correcto

# Permitir peticiones desde tu front-end de React (ej. localhost:3000)
CORS(app, resources={r"/api/*": {"origins": "*"}}) # Puedes cambiar "*" a "http://localhost:3000"

# --- Variables Globales (Estado del Sistema) ---
mc = None
puntoVariacion = None
reglaAdaptacion = None

# --- Tarea Periódica (Versión Síncrona con Thread) ---
def periodic_task_sync():
    global puntoVariacion, reglaAdaptacion, mc
    print("Iniciando bucle de adaptación periódica (cada 120s)...")
    
    while True:
        print("\n" + "="*50)
        print(f"INICIANDO NUEVO CICLO DE ADAPTACIÓN (espera de 120s)")
        
        # 1. Instanciar Mapek
        mapek = Mapek()
        
        # 2. Llamar a monitoreo (que dispara el ciclo completo)
        mapek.monitoreo(mc)
        
        # 3. Actualizar el estado global para los endpoints GET
        puntoVariacion = mapek.getConocimiento()
        reglaAdaptacion = mapek.getReglaAdaptacion()
        
        # 4. Generar la visualización del estado actual en cada ciclo
        if puntoVariacion: 
            # Guardar la imagen en el directorio del backend
            img_path = os.path.join(PROJECT_ROOT, 'estado_actual')
            visualizador_grafo.generar_visualizacion_estado(puntoVariacion, mc, nombre_archivo=img_path)
        else:
            print("Ciclo omitido (posiblemente error del LLM).")

        print(f"CICLO COMPLETO. Durmiendo por 120 segundos...")
        print("="*50 + "\n")
        
        # 5. Esperar 2 minutos (versión síncrona)
        time.sleep(120)

# --- Endpoints de la API (Solo JSON) ---

@app.route("/api/estado")
def get_estado_general():
    """ 
    Endpoint principal para el dashboard de React.
    Devuelve toda la info que el dashboard necesita en una sola llamada. 
    """
    if reglaAdaptacion is None:
         return jsonify({"error": "El sistema está arrancando. Espere al primer ciclo."}), 503
         
    return jsonify({
        "contexto": reglaAdaptacion,
        # Proporciona las rutas de API para que el front-end las consuma
        "imagen_estado_url": "/api/static/estado_actual.png", 
        "imagen_modelo_url": "/api/static/modelo_caracteristicas.png"
    })

@app.route("/api/logs")
def get_logs():
    """ Devuelve los logs como un objeto JSON. """
    log_path = os.path.join(PROJECT_ROOT, 'cambios.log')
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            return jsonify({"log_content": f.read()})
    except FileNotFoundError:
        return jsonify({"log_content": "No se ha registrado ningún cambio todavía."})

@app.route("/api/static/<path:filename>")
def static_files(filename):
    """ Sirve los archivos generados (imágenes) desde el directorio del backend. """
    return send_from_directory(PROJECT_ROOT, filename)

# --- Endpoints de tu API original (adaptados a Flask) ---

@app.route("/api/links")
def get_links(name : str):
    if not puntoVariacion:
        return jsonify({"error": "El sistema está arrancando."}), 503
    return jsonify(puntoVariacion.obtenerConfiguracionNivel(name))

@app.route("/api/link")
def get_link(name : str):
    if not puntoVariacion:
        return jsonify({"error": "El sistema está arrancando."}), 503
    return jsonify(puntoVariacion.obtenerEstadoCaracteristica(name))

@app.route("/api/reglaAdaptacion")
def get_regla_adaptacion():
    if reglaAdaptacion is None:
         return jsonify({"regla_adaptacion_actual": "N/A (esperando primer ciclo)"}), 503
    return jsonify({"contexto_de_entrada": reglaAdaptacion})


# --- Arranque del Servidor ---
if __name__ == '__main__':
    print("Iniciando aplicación Flask...")
    
    # 1. Cargar el Modelo de Características
    mc = grafo_mc.generarPosiblesEstados() 
    
    # 2. Generar la imagen del MODELO
    try:
        model_img_path = os.path.join(PROJECT_ROOT, 'modelo_caracteristicas')
        visualizador_grafo.generar_visualizacion_modelo(
            mc, nombre_archivo=model_img_path
        )
        print("Visualización del modelo estático generada.")
    except Exception as e:
        print(f"[startup] Error al generar la visualización del modelo: {e}")
    
    # 3. Iniciar el bucle MAPE-K en un hilo separado
    # daemon=True asegura que el hilo se cierre cuando cerremos la app
    mapek_thread = threading.Thread(target=periodic_task_sync, daemon=True)
    mapek_thread.start()
    
    # 4. Iniciar el servidor Flask
    print(f"Iniciando servidor Flask en http://127.0.0.1:8000")
    app.run(port=8000, debug=False) # 'debug=True' puede causar problemas con threading