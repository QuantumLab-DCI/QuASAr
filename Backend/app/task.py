import os
from app.core.mapek import Mapek
from app.services import visualizador_grafo
from app import app_path

# Importamos el módulo 'app' para actualizar las variables globales
import app as app_globals

# --- NUEVO: Función para borrar evidencia antigua ---
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
    print("\n" + "="*50)
    print(f"⚡ EVENTO RECIBIDO: Iniciando ciclo único para Escenario ID {escenario_id}")
    
    # 1. LIMPIEZA PREVIA (Crucial para tu problema)
    _limpiar_evidencia_previa()
    
    try:
        # 2. Instanciar Mapek
        mapek = Mapek()
        
        # 3. Ejecutar la lógica manual pasando el ID del escenario
        # (Este método 'ejecutar_escenario_manual' lo definimos en el paso anterior en mapek.py)
        mapek.ejecutar_escenario_manual(mc, escenario_id)
        
        # 4. Actualizar el estado global para que el frontend pueda leerlo
        app_globals.pv_global = mapek.getConocimiento()
        app_globals.regla_global = mapek.getReglaAdaptacion()
        
        # 5. Generar la visualización del estado actual (Grafo verde/rojo)
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
    
    # --- NUEVO: Bloque FINALLY para asegurar desbloqueo ---
    finally:
        app_globals.en_ejecucion = False
        print(f"🔓 SISTEMA LIBERADO: Ciclo finalizado. Listo para recibir instrucciones.")
    # -----------------------------------------------------

    print(f"✅ CICLO COMPLETADO. El sistema vuelve a estado de espera.")
    print("="*50 + "\n")