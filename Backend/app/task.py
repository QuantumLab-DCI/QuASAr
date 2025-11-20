import time
import threading
import os
from app.core.mapek import Mapek
from app.services import visualizador_grafo
from app import app_path

# --- INICIO DE MODIFICACIÓN ---
# Importamos el módulo 'app' (que contiene las variables)
import app as app_globals
# --- FIN DE MODIFICACIÓN ---


def setup_background_tasks(mc):
    """
    Inicia el bucle MAPE-K en un hilo de fondo.
    """
    print("Iniciando bucle de adaptación periódica (cada 10s)...")
    mapek_thread = threading.Thread(target=periodic_task_sync, args=(mc,), daemon=True)
    mapek_thread.start()

def periodic_task_sync(mc):
    """
    El bucle principal de MAPE-K.
    """
    
    while True:
        print("\n" + "="*50)
        print(f"INICIANDO NUEVO CICLO DE ADAPTACIÓN")
        
        # 1. Instanciar Mapek
        mapek = Mapek()
        
        # 2. Llamar a monitoreo (que ahora lee el escenario seleccionado)
        mapek.monitoreo(mc)
        
        # --- INICIO DE MODIFICACIÓN ---
        # 3. Actualizar el estado global usando la referencia del módulo
        app_globals.pv_global = mapek.getConocimiento()
        app_globals.regla_global = mapek.getReglaAdaptacion()
        # --- FIN DE MODIFICACIÓN ---
        
        # 4. Generar la visualización del estado actual en cada ciclo
        if app_globals.pv_global: 
            img_path = os.path.join(app_path, 'data', 'estado_actual')
            visualizador_grafo.generar_visualizacion_estado(app_globals.pv_global, mc, nombre_archivo=img_path)
        else:
            print("Ciclo omitido (posiblemente error del LLM).")

        # 5. Esperar solo 10 segundos para demos interactivas
        print(f"CICLO COMPLETO. Durmiendo por 10 segundos...")
        print("="*50 + "\n")
        time.sleep(10)