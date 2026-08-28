import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
load_dotenv()

# --- Configuración de Rutas ---
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from app import create_app, setup_startup_tasks
from app.core.state import state_manager
from app.config import DEFAULT_HOST, DEFAULT_PORT

if __name__ == '__main__':
    
    print("🚀 Iniciando Backend HQC (Modo Interactivo)...")
    
    # 1. Crear la instancia de la aplicación Flask y obtener el MC
    app, mc = create_app()

    # 2. Ejecutar las tareas de inicio (Solo genera la imagen del modelo estático una vez)
    setup_startup_tasks(mc)

    # 3. Iniciar el servidor Flask
    print(f"✅ Servidor listo en http://{DEFAULT_HOST}:{DEFAULT_PORT}")
    print(f"   Esperando interacción del usuario...")
    
    app.run(port=DEFAULT_PORT, debug=False, host=DEFAULT_HOST)