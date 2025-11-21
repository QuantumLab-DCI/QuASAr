import os
from app.core.mapek import Mapek
from app.services import visualizador_grafo
from app import app_path

# Importamos el módulo 'app' para actualizar las variables globales
import app as app_globals

def ejecutar_ciclo_bajo_demanda(mc, escenario_id):
    """
    Ejecuta UNA sola iteración del ciclo MAPE-K para el escenario solicitado.
    Esta función es llamada por el endpoint '/api/seleccionar_escenario' en un hilo.
    """
    print("\n" + "="*50)
    print(f"⚡ EVENTO RECIBIDO: Iniciando ciclo único para Escenario ID {escenario_id}")
    
    try:
        # 1. Instanciar Mapek
        mapek = Mapek()
        
        # 2. Ejecutar la lógica manual pasando el ID del escenario
        # (Este método 'ejecutar_escenario_manual' lo definimos en el paso anterior en mapek.py)
        mapek.ejecutar_escenario_manual(mc, escenario_id)
        
        # 3. Actualizar el estado global para que el frontend pueda leerlo
        app_globals.pv_global = mapek.getConocimiento()
        app_globals.regla_global = mapek.getReglaAdaptacion()
        
        # 4. Generar la visualización del estado actual (Grafo verde/rojo)
        if app_globals.pv_global: 
            img_path = os.path.join(app_path, 'data', 'estado_actual')
            visualizador_grafo.generar_visualizacion_estado(app_globals.pv_global, mc, nombre_archivo=img_path)
            print("✅ Visualización de estado actualizada.")
        else:
            print("⚠️ Ciclo finalizado sin configuración válida (posible error del LLM).")

    except Exception as e:
        print(f"❌ ERROR CRÍTICO EN TAREA DE FONDO: {e}")
        import traceback
        traceback.print_exc()

    print(f"✅ CICLO COMPLETADO. El sistema vuelve a estado de espera.")
    print("="*50 + "\n")