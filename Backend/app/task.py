import traceback
import os
from app.core.mapek import Mapek
from app.services import visualizador_grafo
from app.config import APP_PATH, STATE_IMAGE_DIR
from app.core.state import state_manager
from app.services.file_service import FileService

# --- NUEVO: Importar el logger de auditoría ---
from app.core.audit_logger import get_logger 
# ----------------------------------------------

def ejecutar_ciclo_bajo_demanda(mc, escenario_id):
    """
    Ejecuta UNA sola iteración del ciclo MAPE-K para el escenario solicitado.
    Esta función es llamada por el endpoint '/api/seleccionar_escenario' en un hilo.
    """
    # 1. Configuración de Auditoría
    logger = get_logger()
    
    # Incrementamos el contador global y capturamos el número del caso actual
    state_manager.increment_counter()
    caso_n = state_manager.get_counter()
    
    # Log de Inicio
    logger.info(f"🔰 --- INICIO CASO #{caso_n} | ESCENARIO ID: {escenario_id} ---")
    
    print("\n" + "="*50)
    print(f"⚡ EVENTO RECIBIDO: Iniciando ciclo único para Escenario ID {escenario_id} (Caso #{caso_n})")
    
    # 2. LIMPIEZA PREVIA
    FileService.clear_evidence_files()
    
    try:
        # 3. Instanciar Mapek
        mapek = Mapek()
        
        # 4. Ejecutar la lógica manual pasando el ID del escenario Y el número de caso
        mapek.ejecutar_escenario_manual(mc, escenario_id, caso_n)
        
        # 5. Actualizar el estado global para que el frontend pueda leerlo
        state_manager.set_pv(mapek.getConocimiento())
        state_manager.set_regla_adaptacion(mapek.getReglaAdaptacion())
        
        # Guardar la traza de ejecución en la variable global
        state_manager.set_trace(mapek.getTrace())
        print(f"📝 TRAZA GUARDADA: {len(state_manager.get_trace())} pasos registrados para visualización.")
        
        # 6. Generar la visualización del estado actual (Grafo verde/rojo)
        pv = state_manager.get_pv()
        if pv: 
            img_path = STATE_IMAGE_DIR
            visualizador_grafo.generar_visualizacion_estado(pv, mc, nombre_archivo=img_path)
            
            # Log de Éxito
            logger.info(f"✅ [CASO #{caso_n}] Ciclo finalizado exitosamente. Visualización generada.")
            print("✅ Visualización de estado actualizada.")
        else:
            # Log de Advertencia
            logger.warning(f"⚠️ [CASO #{caso_n}] Ciclo finalizado sin configuración válida (posible error del LLM).")
            print("⚠️ Ciclo finalizado sin configuración válida.")

    except Exception as e:
        # Log de Error Crítico con Traceback
        logger.error(f"❌ [CASO #{caso_n}] ERROR CRÍTICO EN TAREA: {str(e)}", exc_info=True)
        print(f"❌ ERROR CRÍTICO EN TAREA DE FONDO: {e}")
        traceback.print_exc()
    
    # --- Bloque FINALLY para asegurar desbloqueo y cierre de log ---
    finally:
        state_manager.set_running(False)
        logger.info(f"🏁 --- FIN CASO #{caso_n} ---")
        print(f"🔓 SISTEMA LIBERADO: Ciclo finalizado. Listo para recibir instrucciones.")
    # -----------------------------------------------------

    print(f"✅ CICLO COMPLETADO. El sistema vuelve a estado de espera.")
    print("="*50 + "\n")