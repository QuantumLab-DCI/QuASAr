import logging
import os
from pathlib import Path

# --- Configuración de rutas independiente ---
# Esto evita importar 'app' para prevenir errores circulares
# Ruta actual: Backend/app/core/audit_logger.py
# .parent -> core
# .parent.parent -> app
# .parent.parent.parent -> Backend (Raíz del proyecto)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_FILE = os.path.join(BASE_DIR, 'data', 'auditoria_hqc.log')

def get_logger():
    """Configura y devuelve el logger de auditoría."""
    # Asegurar que el directorio data existe
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    logger = logging.getLogger("audit_hqc")
    
    # Patrón Singleton: Si ya tiene handlers, no los volvemos a agregar
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Formato: [FECHA] [NIVEL] MENSAJE
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        
        # Handler de archivo
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Handler de consola (para ver logs en la terminal al ejecutar run.py)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger