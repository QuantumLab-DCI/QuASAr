import os
from app.core.mapek import Mapek
from app.services import visualizador_grafo
from app import app_path

# Importamos el módulo 'app' para actualizar las variables globales
import app as app_globals

# --- Función para borrar evidencia antigua ---
def _limpiar_evidencia_previa():
    """Elimina imágenes de circuitos anteriores para evitar que el frontend muestre datos viejos."""
    archivos_a_borrar = [
        "qiskit_circuit_evidence.png",
        "cirq_circuit_evidence.png",
        "cirq_convergence_evidence.png"
    ]
    data_dir = os.path.join(app_path, 'data')
    
    print("🧹 TASK: Limpiando evidencia visual antigua...")
    for archivo in archivos_a_borrar:
        ruta_completa = os.path.join(data_dir, archivo)
        if os.path.exists(ruta_completa):
            try:
                os.remove(ruta_completa)
            except Exception as e:
                print(f"   ⚠️ No se pudo borrar {archivo}: {e}")
# ----------------------------------------------------

def ejecutar_ciclo_bajo_demanda(mc, escenario_id):
    """
    Ejecuta UNA sola iteración del ciclo MAPE-K para el escenario solicitado.
    Esta función es llamada por el endpoint '/api/seleccionar_escenario' en un hilo.
    """
    
    # --- CAMBIO 1: Gestión del Contador de Casos ---
    # Incrementamos el contador global definido en __init__.py
    app_globals.execution_counter += 1
    case_num = app_globals.execution_counter
    # -----------------------------------------------

    print("\n" + "="*50)
    print(f"⚡ CASO #{case_num}: Iniciando ciclo para Escenario ID {escenario_id}")
    
    # 1. LIMPIEZA PREVIA
    _limpiar_evidencia_previa()
    
    mapek = None # Inicializamos variable por seguridad en el bloque except

    try:
        # 2. Instanciar Mapek
        mapek = Mapek()
        
        # 3. Ejecutar la lógica manual pasando el ID del escenario Y EL NÚMERO DE CASO
        # --- CAMBIO 2: Pasamos case_num al método ---
        mapek.ejecutar_escenario_manual(mc, escenario_id, case_num)
        
        # 4. Actualizar el estado global para que el frontend pueda leerlo
        app_globals.pv_global = mapek.getConocimiento()
        app_globals.regla_global = mapek.getReglaAdaptacion()
        
        # --- Guardar la traza de ejecución en la variable global ---
        app_globals.trace_global = mapek.getTrace()
        print(f"📝 TRAZA GUARDADA: {len(app_globals.trace_global)} pasos registrados para visualización.")
        
        # 5. Generar la visualización del estado actual (Grafo verde/rojo)
        if app_globals.pv_global: 
            img_path = os.path.join(app_path, 'data', 'estado_actual')
            visualizador_grafo.generar_visualizacion_estado(app_globals.pv_global, mc, nombre_archivo=img_path)
            print("✅ Visualización de estado actualizada.")
        else:
            print("⚠️ Ciclo finalizado sin configuración válida (posible error del LLM).")

    except Exception as e:
        # --- CAMBIO 3: Logging de Error Crítico ---
        print(f"❌ ERROR CRÍTICO EN TAREA DE FONDO: {e}")
        try:
            # Si mapek se instanció, usamos su logger. Si no, instanciamos uno nuevo solo para loguear.
            if mapek is None: mapek = Mapek()
            mapek.registrar_log_archivo("CRITICAL_ERROR", f"Fallo en task.py: {str(e)}")
        except Exception as log_err:
            print(f"   (No se pudo escribir en log file: {log_err})")
        # ------------------------------------------

        import traceback
        traceback.print_exc()
    
    # --- Bloque FINALLY para asegurar desbloqueo ---
    finally:
        app_globals.en_ejecucion = False
        print(f"🔓 SISTEMA LIBERADO: Ciclo finalizado. Listo para recibir instrucciones.")
    # -----------------------------------------------------

    print(f"✅ CICLO #{case_num} COMPLETADO. El sistema vuelve a estado de espera.")
    print("="*50 + "\n")