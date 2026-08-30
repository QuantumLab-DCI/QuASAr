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

# --- Application Configuration ---
app = Flask(__name__)
# Get the absolute path of the script directory
PROJECT_ROOT = Path(__file__).resolve().parent
os.chdir(PROJECT_ROOT) # Ensure the process is in the correct directory

# Allow requests from the React frontend (for example, localhost:3000)
CORS(app, resources={r"/api/*": {"origins": "*"}}) # Change "*" to "http://localhost:3000" if needed

# --- Global Variables (System State) ---
mc = None
puntoVariacion = None
reglaAdaptacion = None

# --- Periodic Task (Synchronous Thread Version) ---
def periodic_task_sync():
    global puntoVariacion, reglaAdaptacion, mc
    print("Iniciando bucle de adaptación periódica (cada 120s)...")
    
    while True:
        print("\n" + "="*50)
        print(f"INICIANDO NUEVO CICLO DE ADAPTACIÓN (espera de 120s)")
        
        # 1. Instantiate Mapek
        mapek = Mapek()
        
        # 2. Call monitoring (which triggers the complete cycle)
        mapek.monitoreo(mc)
        
        # 3. Update global state for the GET endpoints
        puntoVariacion = mapek.getConocimiento()
        reglaAdaptacion = mapek.getReglaAdaptacion()
        
        # 4. Generate the current-state visualization on each cycle
        if puntoVariacion: 
            # Save the image in the backend directory
            img_path = os.path.join(PROJECT_ROOT, 'estado_actual')
            visualizador_grafo.generar_visualizacion_estado(puntoVariacion, mc, nombre_archivo=img_path)
        else:
            print("Ciclo omitido (posiblemente error del LLM).")

        print(f"CICLO COMPLETO. Durmiendo por 120 segundos...")
        print("="*50 + "\n")
        
        # 5. Wait 2 minutes (synchronous version)
        time.sleep(120)

# --- API Endpoints (JSON Only) ---

@app.route("/api/estado")
def get_estado_general():
    """ 
    Main endpoint for the React dashboard.
    Returns all information required by the dashboard in a single call.
    """
    if reglaAdaptacion is None:
         return jsonify({"error": "El sistema está arrancando. Espere al primer ciclo."}), 503
         
    return jsonify({
        "contexto": reglaAdaptacion,
        # Provide API paths for the frontend to consume
        "imagen_estado_url": "/api/static/estado_actual.png", 
        "imagen_modelo_url": "/api/static/modelo_caracteristicas.png"
    })

@app.route("/api/logs")
def get_logs():
    """ Return the logs as a JSON object. """
    log_path = os.path.join(PROJECT_ROOT, 'cambios.log')
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            return jsonify({"log_content": f.read()})
    except FileNotFoundError:
        return jsonify({"log_content": "No se ha registrado ningún cambio todavía."})

@app.route("/api/static/<path:filename>")
def static_files(filename):
    """ Serve generated files (images) from the backend directory. """
    return send_from_directory(PROJECT_ROOT, filename)

# --- Original API Endpoints (Adapted to Flask) ---

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


# --- Server Startup ---
if __name__ == '__main__':
    print("Iniciando aplicación Flask...")
    
    # 1. Load the Feature Model
    mc = grafo_mc.generarPosiblesEstados() 
    
    # 2. Generate the MODEL image
    try:
        model_img_path = os.path.join(PROJECT_ROOT, 'modelo_caracteristicas')
        visualizador_grafo.generar_visualizacion_modelo(
            mc, nombre_archivo=model_img_path
        )
        print("Visualización del modelo estático generada.")
    except Exception as e:
        print(f"[startup] Error al generar la visualización del modelo: {e}")
    
    # 3. Start the MAPE-K loop in a separate thread
    # daemon=True ensures that the thread stops when the application closes
    mapek_thread = threading.Thread(target=periodic_task_sync, daemon=True)
    mapek_thread.start()
    
    # 4. Start the Flask server
    print(f"Iniciando servidor Flask en http://127.0.0.1:8000")
    app.run(port=8000, debug=False) # 'debug=True' may cause threading issues
