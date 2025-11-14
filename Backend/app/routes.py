import os
from flask import jsonify, send_from_directory

# --- INICIO DE MODIFICACIÓN ---
# Importamos el objeto 'app' global y la ruta
from app import app, app_path
# Importamos el módulo 'app' (como 'app_globals') para acceder
# a las variables globales actualizadas por el otro hilo
import app as app_globals
# --- FIN DE MODIFICACIÓN ---


# --- Endpoints de la API (Solo JSON) ---

@app.route("/api/estado")
def get_estado_general():
    """ 
    Endpoint principal para el dashboard de React.
    """
    # --- MODIFICACIÓN AQUÍ ---
    # Leemos la variable a través del módulo 'app_globals'
    if app_globals.regla_global is None:
         return jsonify({"error": "El sistema está arrancando. Espere al primer ciclo."}), 503
         
    return jsonify({
        "contexto": app_globals.regla_global,
        # --- FIN DE MODIFICACIÓN ---
        "imagen_estado_url": "/api/static/estado_actual.png", 
        "imagen_modelo_url": "/api/static/modelo_caracteristicas.png"
    })

@app.route("/api/logs")
def get_logs():
    """ Devuelve los logs como un objeto JSON. """
    log_path = os.path.join(app_path, 'data', 'cambios.log')
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            return jsonify({"log_content": f.read()})
    except FileNotFoundError:
        return jsonify({"log_content": "No se ha registrado ningún cambio todavía."})

@app.route("/api/static/<path:filename>")
def static_files(filename):
    """ Sirve los archivos generados (imágenes) desde el directorio /data. """
    data_dir = os.path.join(app_path, 'data')
    return send_from_directory(data_dir, filename)

# --- Endpoints de tu API original (adaptados a Flask) ---

@app.route("/api/links/<string:name>")
def get_links(name):
    # --- MODIFICACIÓN AQUÍ ---
    if not app_globals.pv_global:
        return jsonify({"error": "El sistema está arrancando."}), 503
    return jsonify(app_globals.pv_global.obtenerConfiguracionNivel(name))

@app.route("/api/link/<string:name>")
def get_link(name):
    # --- MODIFICACIÓN AQUÍ ---
    if not app_globals.pv_global:
        return jsonify({"error": "El sistema está arrancando."}), 503
    return jsonify(app_globals.pv_global.obtenerEstadoCaracteristica(name))

@app.route("/api/reglaAdaptacion")
def get_regla_adaptacion():
    # --- MODIFICACIÓN AQUÍ ---
    if app_globals.regla_global is None:
         return jsonify({"regla_adaptacion_actual": "N/A (esperando primer ciclo)"}), 503
    return jsonify({"contexto_de_entrada": app_globals.regla_global})