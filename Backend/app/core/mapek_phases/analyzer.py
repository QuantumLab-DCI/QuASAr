from typing import Dict, Any, Optional
from app.services import agente_llm
from app.services import hqc_module
from app.core import grafo_mc
from app.core.audit_logger import get_logger
from app.core.state import state_manager

class Analyzer:
    """
    Phase 2: ANALYZE
    Interact with the LLM and validate business and model rules.
    """
    def __init__(self):
        self.logger = get_logger()
        self._razonamiento_actual = "Esperando análisis..."

    def _find_features_in_json(self, data: Dict[str, Any]) -> Dict[str, bool]:
        """Recursively find Boolean features and normalize keys."""
        features = {}
        if isinstance(data, dict):
            for k, v in data.items():
                key_normalizada = k.replace(" ", "_").lower()
                if isinstance(v, bool):
                    features[key_normalizada] = v
                elif isinstance(v, dict):
                    features.update(self._find_features_in_json(v))
        return features

    def _validar_configuracion(self, config_dict: Dict[str, bool], mc) -> bool:
        """
        Validate model rules: Requires, Mandatory, XOR, OR, and Hierarchy.
        """
        # (Logic is identical to the original and was migrated here)
        # For brevity in the agent response, assume the complete logic from the original mapek.py
        # ... [Logic from original mapek.py] ...
        
        # NOTE: To avoid repeating the 50 validation lines, assume this is
        # implemented in the same way as the original. Copy the code in the real implementation.
        
        # 1. Validate 'Requires' dependency rules
        for c in mc.caracteristicas:
            for rel in c.getRelaciones:
                if rel[1] == "Requiere":
                    quien_requiere = c.getNombre.replace(" ", "_").lower()
                    quien_es_requerido = rel[0].replace(" ", "_").lower()
                    if config_dict.get(quien_requiere) and not config_dict.get(quien_es_requerido):
                        return False

        # 2. Validate hierarchy and group constraints (XOR, OR)
        for c in mc.caracteristicas:
            nombre_padre = c.getNombre.replace(" ", "_").lower()
            is_padre_activo = config_dict.get(nombre_padre) == True
            
            hijos_xor = [r[0].replace(" ", "_").lower() for r in c.getRelaciones if r[1] == "XOR"]
            hijos_or = [r[0].replace(" ", "_").lower() for r in c.getRelaciones if r[1] == "OR"]
            
            if is_padre_activo:
                for rel in c.getRelaciones:
                    if rel[1] == "Obligatoria":
                        hijo_key = rel[0].replace(" ", "_").lower()
                        if not config_dict.get(hijo_key): return False
                
                if hijos_xor:
                    activos_xor = sum(1 for h in hijos_xor if config_dict.get(h) == True)
                    if activos_xor != 1: return False
                
                if hijos_or:
                    activos_or = sum(1 for h in hijos_or if config_dict.get(h) == True)
                    if activos_or == 0: return False
            
            elif config_dict.get(nombre_padre) == False:
                 for rel in c.getRelaciones:
                    if rel[1] != "Requiere":
                        hijo_key = rel[0].replace(" ", "_").lower()
                        if config_dict.get(hijo_key) == True: return False

        return True

    def analizar(self, mc, contexto_monitor: Dict[str, Any], caso_n: int) -> Optional[Dict[str, bool]]:
        """
        Query the LLM and return the validated configuration.
        """
        ica = contexto_monitor['ica']
        cp = contexto_monitor['complejidad_problema']
        prioridad = contexto_monitor['prioridad']
        cola = contexto_monitor['cola_qiskit']
        perfil = contexto_monitor['perfil_usuario']
        
        reglas_del_modelo = mc.exportar_reglas_texto()
        metricas_nisq = hqc_module.monitor_backends()
        
        # Queue simulator injection
        if cola is not None:
            metricas_nisq["Qiskit Simulator"]["queue_time_sec"] = cola

        prompt_contexto = f"""
        DATOS DEL ENTORNO EN TIEMPO REAL (Simulación Estocástica - Escenario {state_manager.get_escenario_id()}):
        
        1. **Perfil de Demanda (INTENCIÓN DE USUARIO):** "{perfil}"
        2. **Condiciones Ambientales:** Aire ICA = {ica}.
        3. **Requerimiento Computacional:** Complejidad CP = {cp}.
        4. **Infraestructura:** Prioridad {prioridad}, Backends {metricas_nisq}
        """
        
        config_dict_llm = agente_llm.obtener_configuracion_llm(prompt_contexto, reglas_del_modelo)

        if not config_dict_llm:
            self.logger.error(f"[CASO #{caso_n}] ❌ FALLO LLM: Configuración vacía.")
            return None

        # Capture reasoning
        if "razonamiento" in config_dict_llm:
            self._razonamiento_actual = config_dict_llm["razonamiento"]
            self.logger.info(f"[CASO #{caso_n}] ✅ LLM Respondió. Razonamiento: {self._razonamiento_actual}")

        config_plana = self._find_features_in_json(config_dict_llm)
        
        # --- SELF-REPAIR (Orphaned HQC) ---
        if config_plana.get('hqc') == False:
            nodos_cuanticos = ['backend', 'algoritmo', 'qiskit_simulator', 'cirq_simulator', 'qaoa', 'vqe']
            for nodo in nodos_cuanticos:
                if config_plana.get(nodo) == True:
                    config_plana[nodo] = False

        # Formal validation
        config_plana_con_raiz = config_plana.copy()
        config_plana_con_raiz['gestor_aire'] = True 
        
        if not self._validar_configuracion(config_plana_con_raiz, mc):
            self.logger.error(f"[CASO #{caso_n}] ❌ FALLO VALIDACIÓN: Configuración LLM inválida.")
            return None

        return config_plana

    def get_razonamiento(self):
        return self._razonamiento_actual
