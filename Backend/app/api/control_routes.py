from flask import jsonify, request
from app.core.state import state_manager
from app.task import ejecutar_ciclo_bajo_demanda
import threading

from . import control_bp

@control_bp.route("/seleccionar_escenario", methods=['POST'])
def set_escenario():
    """ 
    Permite al usuario elegir un escenario y DISPARA LA EJECUCIÓN INMEDIATA.
    """
    data = request.json
    nuevo_id = data.get('id')
    
    # Bloqueo de seguridad
    if state_manager.is_running():
        return jsonify({"error": "Sistema ocupado. Espere a que finalice el ciclo actual."}), 423 
    
    if nuevo_id is not None:
        try:
            # 1. Actualizar variable global (Memoria)
            act_id = int(nuevo_id)
            state_manager.set_escenario_id(act_id)
            
            print(f"🕹️ INTERACCIÓN: Usuario seleccionó Escenario ID {act_id}")

            # Bloquear sistema
            state_manager.set_running(True)
            print(f"🔒 SISTEMA BLOQUEADO: Iniciando ciclo MAPE-K para Escenario {act_id}")

            # 2. DISPARAR EL EVENTO (Threading)
            # Pasamos solo el ID, ya que el MC se obtiene del state_manager dentro de la task si es necesario
            # o se pasa aqui. El task original recibia mc.
            # Vamos a refactorizar task para que use state_manager tambien.
            
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
