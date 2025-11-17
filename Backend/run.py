import os
import sys # <-- Importación necesaria
from dotenv import load_dotenv
load_dotenv() # <-- AÑADIDO: Carga las variables del .env
from app import create_app, setup_startup_tasks, setup_background_tasks 
from pathlib import Path

# --- INICIO DE CORRECCIÓN ---
# 1. Aseguramos que el directorio actual (Backend) esté en el Python Path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# 2. Reafirmamos el directorio de trabajo (aunque ya lo hace la línea anterior)
os.chdir(PROJECT_ROOT)
# --- FIN DE CORRECCIÓN ---

# --- Configuración y Arranque ---
if __name__ == '__main__':
    
    print("Iniciando aplicación Flask desde run.py...")
    
    # 1. Crear la instancia de la aplicación Flask y obtener el Modelo de Características (mc)
    app, mc = create_app()

    # 2. Ejecutar las tareas de inicio (generar imagen del modelo estático)
    setup_startup_tasks(mc)

    # 3. Iniciar el bucle MAPE-K en un hilo separado
    setup_background_tasks(mc)

    # 4. Iniciar el servidor Flask
    print(f"Servidor Flask iniciado en http://0.0.0.0:8000")
    app.run(port=8000, debug=False, host='0.0.0.0')