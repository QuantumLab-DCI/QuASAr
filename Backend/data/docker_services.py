"""Run a simulated service activity loop and status server."""

import http.server
import logging
import os
import random
import socketserver
import sys
import threading
import time
from datetime import datetime

PORT = int(os.environ.get("PORT", 80))
SERVICE_NAME = os.environ.get("SERVICE_NAME", "Base Service")
THEME_COLOR = os.environ.get("THEME_COLOR", "#333333")
LOG_FILE = "service.log"

# Emit logs to container output and the file served by this process.
logger = logging.getLogger(SERVICE_NAME)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler(LOG_FILE, mode='a')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def simulate_service_activity():
    """Generate background activity consistent with the service."""
    logger.info("%s started successfully. PID: %s", SERVICE_NAME, os.getpid())
    logger.info("Connected to the event bus.")

    while True:
        try:
            time.sleep(random.uniform(2, 8))

            if "tourism" in SERVICE_NAME.lower():
                actions = [
                    f"Querying the points-of-interest database (query ID: {random.randint(1000,9999)})",
                    "Updating guide availability for the volcano zone.",
                    f"Computing an optimal route for user {random.randint(50,500)}.",
                    "Synchronizing with the weather API.",
                ]
                logger.info(random.choice(actions))

            elif "sports" in SERVICE_NAME.lower():
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

# The daemon stops with the server process.
background_thread = threading.Thread(target=simulate_service_activity, daemon=True)
background_thread.start()

class RealLogHandler(http.server.SimpleHTTPRequestHandler):
    """Serve service status and route requests through the logger."""

    def log_message(self, format, *args):
        """Route access messages through the configured logger."""
        logger.info("HTTP request: %s - %s", self.client_address[0], format % args)

    def do_GET(self):
        """Return the simulated service status page."""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')  # Required by the iframe.
        self.end_headers()

        uptime = int(time.time()) % 1000
        memory_mb = random.randint(12, 64)

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

logger.info("Starting the web server on port %s.", PORT)
with socketserver.TCPServer(("", PORT), RealLogHandler) as httpd:
    httpd.serve_forever()
