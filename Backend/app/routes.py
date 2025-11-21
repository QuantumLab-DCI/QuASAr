import os
import json
import threading # <--- Necesario para la ejecución inmediata
from flask import jsonify, send_from_directory, request
from app import app, app_path
import app as app_globals

# Importamos el módulo de tareas para poder disparar el ciclo manualmente
from app import task 

# --- Endpoints de la API ---

@app.route("/api/estado")
def get_estado_general():
    """ 
    Endpoint principal para el dashboard.
    Devuelve el contexto, la configuración activa y la evidencia visual.
    """
    if app_globals.regla_global is None:
         return jsonify({"error": "El sistema está arrancando. Seleccione un escenario."}), 503
    
    evidencia_cuantica = None
    
    # Rutas de evidencia
    qiskit_evidence = "/api/static/qiskit_circuit_evidence.png"
    cirq_circuit_png = "/api/static/cirq_circuit_evidence.png"
    cirq_convergence_png = "/api/static/cirq_convergence_evidence.png"
    
    # Usamos ruta absoluta para evitar ambigüedad
    data_dir = os.path.abspath(os.path.join(app_path, 'data'))

    # Prioridad de visualización de evidencia
    if os.path.exists(os.path.join(data_dir, "qiskit_circuit_evidence.png")):
        evidencia_cuantica = qiskit_evidence
    elif os.path.exists(os.path.join(data_dir, "cirq_circuit_evidence.png")):
        evidencia_cuantica = cirq_circuit_png
    elif os.path.exists(os.path.join(data_dir, "cirq_convergence_evidence.png")):
        evidencia_cuantica = cirq_convergence_png

    return jsonify({
        "contexto": app_globals.regla_global,
        "escenario_actual_id": app_globals.escenario_activo_id, 
        "imagen_estado_url": "/api/static/estado_actual.png", 
        "imagen_modelo_url": "/api/static/modelo_caracteristicas.png",
        "evidencia_cuantica_url": evidencia_cuantica
    })

# --- ENDPOINTS INTERACTIVOS ---

@app.route("/api/escenarios", methods=['GET'])
def get_escenarios():
    """ Devuelve la lista de escenarios desde el JSON. """
    try:
        json_path = os.path.join(app_path, 'data', 'scenarios.json')
        if not os.path.exists(json_path):
            return jsonify([]) 
            
        with open(json_path, 'r', encoding='utf-8') as f:
            scenarios = json.load(f)
        return jsonify(scenarios)
    except Exception as e:
        return jsonify({"error": f"Error cargando escenarios: {e}"}), 500

@app.route("/api/seleccionar_escenario", methods=['POST'])
def set_escenario():
    """ 
    Permite al usuario elegir un escenario y DISPARA LA EJECUCIÓN INMEDIATA.
    """
    data = request.json
    nuevo_id = data.get('id')
    
    if nuevo_id is not None:
        try:
            # 1. Actualizar variable global (Memoria)
            act_id = int(nuevo_id)
            app_globals.escenario_activo_id = act_id
            
            print(f"🕹️ INTERACCIÓN: Usuario seleccionó Escenario ID {act_id}")

            # 2. DISPARAR EL EVENTO (Threading)
            # Esto ejecuta el ciclo MAPE-K en segundo plano inmediatamente
            # sin bloquear la respuesta HTTP al frontend.
            # Pasamos app_globals.mc_global que se cargó en __init__.py
            thread = threading.Thread(
                target=task.ejecutar_ciclo_bajo_demanda,
                args=(app_globals.mc_global, act_id)
            )
            thread.start()

            return jsonify({
                "status": "ok", 
                "mensaje": f"Escenario {act_id} activado. Ejecutando ciclo...", 
                "id": act_id
            })
        except ValueError:
            return jsonify({"error": "ID debe ser un número"}), 400
        except Exception as e:
             print(f"❌ Error lanzando hilo: {e}")
             return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Falta el ID"}), 400

# --- Endpoints de Soporte ---

@app.route("/api/logs")
def get_logs():
    log_path = os.path.join(app_path, 'data', 'cambios.log')
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            return jsonify({"log_content": f.read()})
    except FileNotFoundError:
        return jsonify({"log_content": "Esperando primera ejecución..."})

@app.route("/api/static/<path:filename>")
def static_files(filename):
    """ Sirve los archivos generados (imágenes) desde el directorio /data. """
    # Usar ruta absoluta es más seguro
    data_dir = os.path.abspath(os.path.join(app_path, 'data'))
    
    try:
        response = send_from_directory(data_dir, filename)
        # Desactivar caché para que las imágenes se actualicen al instante
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        # Manejo de errores si el archivo no existe aún
        return jsonify({"error": "Archivo no encontrado"}), 404

# --- Endpoints Legacy (Opcionales) ---

@app.route("/api/links/<string:name>")
def get_links(name):
    if not app_globals.pv_global:
        return jsonify({"error": "Sistema arrancando."}), 503
    return jsonify(app_globals.pv_global.obtenerConfiguracionNivel(name))

@app.route("/api/link/<string:name>")
def get_link(name):
    if not app_globals.pv_global:
        return jsonify({"error": "Sistema arrancando."}), 503
    return jsonify(app_globals.pv_global.obtenerEstadoCaracteristica(name))

@app.route("/api/reglaAdaptacion")
def get_regla_adaptacion():
    if app_globals.regla_global is None:
         return jsonify({"regla_adaptacion_actual": "N/A"}), 503
    return jsonify({"contexto_de_entrada": app_globals.regla_global})