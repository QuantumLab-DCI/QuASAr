from flask import jsonify, request
from app.core.state import state_manager
from app.task import ejecutar_ciclo_bajo_demanda
import threading

from . import control_bp

@control_bp.route("/seleccionar_escenario", methods=['POST'])
def set_escenario():
    """ 
    Allow the user to select a scenario and TRIGGER IMMEDIATE EXECUTION.
    """
    data = request.json
    nuevo_id = data.get('id')
    
    # Safety lock
    if state_manager.is_running():
        return jsonify({"error": "Sistema ocupado. Espere a que finalice el ciclo actual."}), 423 
    
    if nuevo_id is not None:
        try:
            # 1. Update the global variable (memory)
            act_id = int(nuevo_id)
            state_manager.set_escenario_id(act_id)
            
            print(f"🕹️ INTERACCIÓN: Usuario seleccionó Escenario ID {act_id}")

            # Lock the system
            state_manager.set_running(True)
            print(f"🔒 SISTEMA BLOQUEADO: Iniciando ciclo MAPE-K para Escenario {act_id}")

            # 2. TRIGGER THE EVENT (Threading)
            # Pass only the ID because the task obtains the feature model from
            # state_manager if needed. The original task received mc directly.
            # Refactor the task to use state_manager as well.
            
            thread = threading.Thread(
                target=ejecutar_ciclo_bajo_demanda,
                args=(state_manager.get_mc(), act_id)
            )
            thread.start()

            return jsonify({
                "status": "ok", 
                "mensaje": f"Escenario {act_id} activado. Ejecutando ciclo...", 
                "id": act_id
            })
        except ValueError:
            return jsonify({"error": "ID debe ser un número"}), 400
        except Exception as e:
             print(f"❌ Error lanzando hilo: {e}")
             state_manager.set_running(False)
             return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Falta el ID"}), 400
