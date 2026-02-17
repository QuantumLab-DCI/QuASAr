import os
import time
import datetime
from typing import Dict, Any, List
from app.services.docker_service import DockerService
from app.services import hqc_module
from app.config import LOG_FILE
from app.core.state import state_manager
from app.core.audit_logger import get_logger

class Executor:
    """
    Fase 4: EXECUTE
    Responsable de aplicar los cambios en la infraestructura (Docker) y ejecutar algoritmos cuánticos.
    """
    def __init__(self):
        self.logger = get_logger()
        self.docker_service = DockerService()
        self.log_path = LOG_FILE

    def ejecutar(self, plan_contenedores: Dict[str, bool], caso_n: int, contexto: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Ejecuta los cambios planificados y retorna una traza de ejecución.
        """
        trace_pasos = []

        if not plan_contenedores:
             return trace_pasos

        self.logger.info(f"[CASO #{caso_n}] ⚙️ Iniciando reconfiguración de infraestructura...")

        # 1. Ejecución Docker (Infraestructura)
        client = self.docker_service.client
        
        # Logs de cambios físicos
        with open(self.log_path, "a", encoding="utf-8") as log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"\n--- RECONFIGURACIÓN {timestamp} ---\n")
            
            containers_list = self.docker_service.list_containers(all=True)
            
            for container in containers_list:
                estado_deseado = plan_contenedores.get(container.name)
                if estado_deseado is not None:
                    try:
                        cont = self.docker_service.get_container(container.id)
                        
                        if estado_deseado == True and cont.status == "exited":
                            cont.start()
                            log_file.write(f"[+] Contenedor '{container.name}' iniciado.\n")
                            self.logger.info(f"[CASO #{caso_n}] 🟢 ACTIVADO EXITO: Contenedor '{container.name}'")
                            
                        elif estado_deseado == False and cont.status == "running":
                            cont.stop()
                            log_file.write(f"[-] Contenedor '{container.name}' detenido.\n")
                            self.logger.info(f"[CASO #{caso_n}] 🔴 DESACTIVADO EXITO: Contenedor '{container.name}'")
                            
                    except Exception as e:
                        msg_err = f"EXECUTE_ERROR Docker en {container.name}: {e}"
                        print(msg_err)
                        accion = "ACTIVAR" if estado_deseado else "DESACTIVAR"
                        self.logger.error(f"[CASO #{caso_n}] ❌ ERROR AL {accion} nodo '{container.name}': {str(e)}")

        # 2. Ejecución Cuántica (Adaptativa) - Si HQC está activo
        if plan_contenedores.get("hqc") == True:
            trace_hqc = self._ejecutar_hqc(plan_contenedores, caso_n, contexto)
            if trace_hqc:
                trace_pasos.append(trace_hqc)
        
        return trace_pasos

    def _ejecutar_hqc(self, contenedores: Dict[str, bool], caso_n: int, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sub-rutina para manejar la ejecución de algoritmos cuánticos si es necesario.
        """
        algoritmo_qaoa_activo = contenedores.get("qaoa") == True
        algoritmo_vqe_activo = contenedores.get("vqe") == True

        if algoritmo_qaoa_activo or algoritmo_vqe_activo:
            try:
                # Determinar Backend
                backend_key = next((b for b in ["qiskit_simulator", "cirq_simulator"] if contenedores.get(b)), None)
                if not backend_key:
                     return None # HQC activo pero sin backend seleccionado (raro, pero posible si validación fallara)

                algoritmo = "QAOA" if algoritmo_qaoa_activo else "VQE"
                backend_nombre = backend_key.replace("_", " ").title()

                # Adaptación de Carga (Basado en CP monitoreado)
                # OJO: Necesitamos 'cp' del contexto. Se asume que viene en 'contexto'
                cp = contexto.get('complejidad_problema', 100)
                
                if cp < 250:
                    problem_size = 3
                else:
                    problem_size = 4 

                circuit_depth = 1
                if cp >= 400:
                    circuit_depth = 2
                
                # Ejecutar
                backend_adapter = hqc_module.get_backend_adapter(backend_nombre)

                if backend_adapter:
                    unique_id = f"{state_manager.get_escenario_id()}_{int(time.time())}"
                    params = {
                        "problema_id": unique_id,
                        "complejidad_cp": cp,
                        "size": problem_size,    
                        "depth": circuit_depth   
                    }
                    
                    self.logger.info(f"[CASO #{caso_n}] ⚛️ Iniciando Job HQC en {backend_nombre} ({algoritmo})...")
                    resultado = backend_adapter.execute_job(algoritmo=algoritmo, params=params)
                    
                    with open(self.log_path, "a", encoding="utf-8") as log_file:
                            log_file.write(f"[⚛️] Job HQC: Costo={resultado.get('costo_optimo')}\n")
                    
                    self.logger.info(f"[CASO #{caso_n}] ⚛️ EXITO HQC: Job completado. Costo={resultado.get('costo_optimo')}")

                    return {
                        "fase": "FIN EJECUCIÓN HQC",
                        "mensaje": "Trabajo cuántico finalizado.",
                        "detalles": {
                            "Costo Óptimo": f"{resultado.get('costo_optimo'):.4f}",
                            "Evidencia": "Generada en /data",
                            "Backend": backend_nombre
                        }
                    }

            except Exception as e:
                print(f"EXECUTE_ERROR HQC: {e}")
                self.logger.error(f"[CASO #{caso_n}] ❌ FALLO HQC: Error en ejecución cuántica: {str(e)}")
                return {
                     "fase": "ERROR",
                     "mensaje": f"Fallo en ejecución cuántica: {e}"
                }
        return None
