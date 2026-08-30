import traceback
import os
from app.core.mapek import Mapek
from app.services import visualizador_grafo
from app.config import APP_PATH, STATE_IMAGE_DIR
from app.core.state import state_manager
from app.services.file_service import FileService

# --- NEW: Import the audit logger ---
from app.core.audit_logger import get_logger 
# ----------------------------------------------

def ejecutar_ciclo_bajo_demanda(mc, escenario_id):
    """
    Execute a single MAPE-K cycle iteration for the requested scenario.
    This function is called in a thread by the '/api/seleccionar_escenario' endpoint.
    """
    # 1. Audit configuration
    logger = get_logger()
    
    # Increment the global counter and capture the current case number
    state_manager.increment_counter()
    caso_n = state_manager.get_counter()
    
    # Start log
    logger.info(f"🔰 --- INICIO CASO #{caso_n} | ESCENARIO ID: {escenario_id} ---")
    
    print("\n" + "="*50)
    print(f"⚡ EVENTO RECIBIDO: Iniciando ciclo único para Escenario ID {escenario_id} (Caso #{caso_n})")
    
    # 2. PRELIMINARY CLEANUP
    FileService.clear_evidence_files()
    
    try:
        # 3. Instantiate Mapek
        mapek = Mapek()
        
        # 4. Execute the manual logic with the scenario ID and case number
        mapek.ejecutar_escenario_manual(mc, escenario_id, caso_n)
        
        # 5. Update global state so the frontend can read it
        state_manager.set_pv(mapek.getConocimiento())
        state_manager.set_regla_adaptacion(mapek.getReglaAdaptacion())
        
        # Store the execution trace in the global variable
        state_manager.set_trace(mapek.getTrace())
        print(f"📝 TRAZA GUARDADA: {len(state_manager.get_trace())} pasos registrados para visualización.")
        
        # 6. Generate the current-state visualization (green/red graph)
        pv = state_manager.get_pv()
        if pv: 
            img_path = STATE_IMAGE_DIR
            visualizador_grafo.generar_visualizacion_estado(pv, mc, nombre_archivo=img_path)
            
            # Success log
            logger.info(f"✅ [CASO #{caso_n}] Ciclo finalizado exitosamente. Visualización generada.")
            print("✅ Visualización de estado actualizada.")
        else:
            # Warning log
            logger.warning(f"⚠️ [CASO #{caso_n}] Ciclo finalizado sin configuración válida (posible error del LLM).")
            print("⚠️ Ciclo finalizado sin configuración válida.")

    except Exception as e:
        # Critical error log with traceback
        logger.error(f"❌ [CASO #{caso_n}] ERROR CRÍTICO EN TAREA: {str(e)}", exc_info=True)
        print(f"❌ ERROR CRÍTICO EN TAREA DE FONDO: {e}")
        traceback.print_exc()
    
    # --- FINALLY block to ensure unlocking and log closure ---
    finally:
        state_manager.set_running(False)
        logger.info(f"🏁 --- FIN CASO #{caso_n} ---")
        print(f"🔓 SISTEMA LIBERADO: Ciclo finalizado. Listo para recibir instrucciones.")
    # -----------------------------------------------------

    print(f"✅ CICLO COMPLETADO. El sistema vuelve a estado de espera.")
    print("="*50 + "\n")
