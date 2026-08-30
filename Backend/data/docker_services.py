import http.server
import logging
import os
import random
import socketserver
import sys
import threading
import time
from datetime import datetime

# --- CONFIGURATION ---
PORT = int(os.environ.get("PORT", 80))
SERVICE_NAME = os.environ.get("SERVICE_NAME", "Base Service")
THEME_COLOR = os.environ.get("THEME_COLOR", "#333333")
LOG_FILE = "service.log"

# --- 1. CONFIGURE REAL LOGGING (Console + File) ---
# This makes logs appear both in Docker Desktop and in the internal file
logger = logging.getLogger(SERVICE_NAME)
logger.setLevel(logging.DEBUG)

# Production-style format: [TIME] [LEVEL] [THREAD] MESSAGE
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')

# Console output (Docker logs)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File output (for reading with 'tail -f' inside the container)
file_handler = logging.FileHandler(LOG_FILE, mode='a')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# --- 2. BUSINESS PROCESS SIMULATION (Background Threads) ---
def simulate_service_activity():
    """Generate background activity consistent with the service."""
    logger.info("%s started successfully. PID: %s", SERVICE_NAME, os.getpid())
    logger.info("Connected to the event bus.")

    while True:
        try:
            time.sleep(random.uniform(2, 8)) # Variable interval

            # Service-specific logic
            if "tourism" in SERVICE_NAME.lower():
                actions = [
                    f"Querying the points-of-interest database (query ID: {random.randint(1000,9999)})",
                    "Updating guide availability for the volcano zone.",
                    f"Computing an optimal route for user {random.randint(50,500)}.",
                    "Synchronizing with the weather API.",
                ]
                logger.info(random.choice(actions))

            elif "sports" in SERVICE_NAME.lower():
                # Simulate sensor readings
                simulated_aqi = random.randint(20, 120)
                level = "CRITICAL" if simulated_aqi > 100 else "NORMAL"
                log_func = logger.warning if simulated_aqi > 100 else logger.info

                logger.debug("Reading sensor IoT_Canopy_01; raw value: %s", random.random())
                log_func("Environmental monitor: AQI=%s status=%s", simulated_aqi, level)

            elif SERVICE_NAME.lower().replace(" ", "_") in {
                "hybrid_quantum_computing",
                "qiskit_simulator",
                "cirq_simulator",
            }:
                actions = [
                    f"Calibrating qubits (fidelity: 99.{random.randint(10,99)}%).",
                    "Clearing the pending-job queue.",
                    f"Received Qiskit backend telemetry: {random.randint(2,15)} ms latency.",
                    "Running surface-code quantum error correction.",
                ]
                logger.info(random.choice(actions))

            elif "air" in SERVICE_NAME.lower():
                logger.info("Sampling remote stations [1/5]: OK.")

            else:
                logger.debug("Heartbeat: system is operational and stable.")

        except Exception as error:
            logger.error("Simulation thread failed: %s", error)

# Start the background thread (daemonized so it stops when the script stops)
background_thread = threading.Thread(target=simulate_service_activity, daemon=True)
background_thread.start()

# --- 3. REAL WEB SERVER (Request Handling) ---
class RealLogHandler(http.server.SimpleHTTPRequestHandler):

    def log_message(self, format, *args):
        # Override this method to use the configured logger instead of default stderr
        logger.info("HTTP request: %s - %s", self.client_address[0], format % args)

    def do_GET(self):
        # Simulate a short processing delay
        # time.sleep(0.05)

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*') # CORS required for the iframe
        self.end_headers()

        # Dynamic data for the HTML
        uptime = int(time.time()) % 1000
        memory_mb = random.randint(12, 64)

        # HTML displayed in the micro-frontend
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
                    Active
                </div>
                <div style="font-size: 12px; color: #666; margin-bottom: 5px;">
                    Uptime: {uptime}s | Memory: {memory_mb} MB
                </div>
                <div style="font-size: 10px; color: #999; font-style: italic;">
                    Last Refreshed: {datetime.now().strftime('%H:%M:%S')}
                </div>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

# --- STARTUP ---
logger.info("Starting the web server on port %s.", PORT)
with socketserver.TCPServer(("", PORT), RealLogHandler) as httpd:
    httpd.serve_forever()
