import http.server
import socketserver
import json
import random
import os
import time
import threading
import logging
import sys
from datetime import datetime

# --- CONFIGURACIÓN ---
PORT = int(os.environ.get("PORT", 80))
SERVICE_NAME = os.environ.get("SERVICE_NAME", "Servicio Base")
THEME_COLOR = os.environ.get("THEME_COLOR", "#333333")
LOG_FILE = "servicio.log"

# --- 1. CONFIGURAR LOGGING REAL (Consola + Archivo) ---
# Esto hace que los logs aparezcan en Docker Desktop Y en el archivo interno
logger = logging.getLogger(SERVICE_NAME)
logger.setLevel(logging.DEBUG)

# Formato profesional: [HORA] [NIVEL] [HILO] MENSAJE
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')

# Salida a Consola (Docker Logs)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Salida a Archivo (Para leer con 'tail -f' dentro del contenedor)
file_handler = logging.FileHandler(LOG_FILE, mode='a')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# --- 2. SIMULACIÓN DE PROCESOS DE NEGOCIO (Hilos de fondo) ---
def tarea_simulada():
    """Genera actividad de fondo coherente con el servicio"""
    logger.info(f"✅ {SERVICE_NAME} iniciado correctamente. PID: {os.getpid()}")
    logger.info("📡 Conectando al bus de eventos... CONECTADO.")
    
    while True:
        try:
            time.sleep(random.uniform(2, 8)) # Intervalo variable
            
            # Lógica específica por servicio
            if "turismo" in SERVICE_NAME.lower():
                acciones = [
                    f"Consultando DB de POIs (Query ID: {random.randint(1000,9999)})",
                    "Actualizando disponibilidad de guías: Zona Volcán",
                    f"Calculando ruta óptima para usuario #{random.randint(50,500)}...",
                    "Sincronizando con API de Clima..."
                ]
                logger.info(random.choice(acciones))
                
            elif "deportes" in SERVICE_NAME.lower():
                # Simular lectura de sensores
                ica_simulado = random.randint(20, 120)
                nivel = "CRÍTICO" if ica_simulado > 100 else "NORMAL"
                log_func = logger.warning if ica_simulado > 100 else logger.info
                
                logger.debug(f"Leyendo sensor IoT_Canopy_01... Valor Raw: {random.random()}")
                log_func(f"Monitor Ambiental: ICA={ica_simulado} Estado={nivel}")
                
            elif "hqc" in SERVICE_NAME.lower():
                acciones = [
                    f"Calibrando Qubits (Fidelidad: 99.{random.randint(10,99)}%)",
                    "Limpiando cola de trabajos pendientes...",
                    f"Recibida telemetría de Backend Qiskit: Latencia {random.randint(2,15)}ms",
                    "Ejecutando corrección de errores cuánticos (Surface Code)..."
                ]
                logger.info(random.choice(acciones))
                
            elif "aire" in SERVICE_NAME.lower():
                logger.info(f"Muestreando estaciones remotas [1/5]... OK")
                
            else:
                logger.debug("Heartbeat: Sistema operativo y estable.")
                
        except Exception as e:
            logger.error(f"Error en hilo de simulación: {e}")

# Iniciar el hilo de fondo (Daemon para que muera si el script muere)
hilo_fondo = threading.Thread(target=tarea_simulada, daemon=True)
hilo_fondo.start()

# --- 3. SERVIDOR WEB REAL (Manejo de Peticiones) ---
class RealLogHandler(http.server.SimpleHTTPRequestHandler):
    
    def log_message(self, format, *args):
        # Sobreescribimos para usar nuestro logger en lugar del stderr por defecto
        logger.info(f"🌐 HTTP Request: {self.client_address[0]} - {format%args}")

    def do_GET(self):
        # Simular pequeño tiempo de procesamiento
        # time.sleep(0.05) 
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*') # CORS vital para Iframe
        self.end_headers()

        # Datos dinámicos para el HTML
        uptime = int(time.time()) % 1000
        memoria = random.randint(12, 64)
        
        # HTML que se ve en el Micro-frontend
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="refresh" content="5"> <style>
                body {{ font-family: 'Courier New', monospace; background: {THEME_COLOR}10; margin: 0; padding: 15px; display: flex; flex-direction: column; height: 100vh; box-sizing: border-box; }}
                .card {{ background: white; border-left: 5px solid {THEME_COLOR}; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-radius: 4px; }}
                h3 {{ margin: 0 0 10px 0; color: {THEME_COLOR}; display: flex; align-items: center; gap: 8px; }}
                .status {{ font-size: 12px; color: #666; margin-top: 10px; border-top: 1px solid #eee; padding-top: 5px; }}
                .live-indicator {{ display: inline-block; width: 8px; height: 8px; background: #2ecc71; border-radius: 50%; animation: blink 1s infinite; }}
                @keyframes blink {{ 50% {{ opacity: 0.4; }} }}
            </style>
        </head>
        <body>
            <div class="card">
                <h3><span class="live-indicator"></span> {SERVICE_NAME}</h3>
                <div style="font-size: 24px; font-weight: bold; color: #333;">
                    Activo
                </div>
                <div style="font-size: 12px; color: #666; margin-bottom: 5px;">
                    Uptime: {uptime}s | Mem: {memoria}MB
                </div>
                <div style="font-size: 10px; color: #999; font-style: italic;">
                    Last Refreshed: {datetime.now().strftime('%H:%M:%S')}
                </div>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

# --- ARRANQUE ---
logger.info(f"🚀 Iniciando servidor web en puerto {PORT}")
with socketserver.TCPServer(("", PORT), RealLogHandler) as httpd:
    httpd.serve_forever()