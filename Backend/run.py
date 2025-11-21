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

# Importar la fábrica de la app y la tarea de inicio estática
# NOTA: Ya no importamos setup_background_tasks porque el sistema ahora es interactivo
from app import create_app, setup_startup_tasks

if __name__ == '__main__':
    
    print("🚀 Iniciando Backend HQC (Modo Interactivo)...")
    
    # 1. Crear la instancia de la aplicación Flask y cargar el modelo (mc)
    app, mc = create_app()

    # 2. Ejecutar las tareas de inicio (Solo genera la imagen del modelo estático una vez)
    setup_startup_tasks(mc)

    # 3. Iniciar el servidor Flask
    # El sistema se quedará esperando peticiones del Frontend en /api/seleccionar_escenario
    print(f"✅ Servidor listo en http://0.0.0.0:8000")
    print(f"   Esperando interacción del usuario...")
    
    app.run(port=8000, debug=False, host='0.0.0.0')