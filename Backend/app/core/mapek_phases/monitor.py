from typing import Dict, Any, List, Optional
import random
import datetime
import os
import json
from app.config import SCENARIOS_JSON
from app.core.audit_logger import get_logger

class Monitor:
    """
    Fase 1: MONITOR
    Responsable de recolectar datos del entorno simulado y perfil de usuario.
    """
    def __init__(self):
        self.logger = get_logger()
        self.scenarios = self._load_scenarios()

    def _load_scenarios(self) -> List[Dict[str, Any]]:
        """Carga los escenarios desde el JSON."""
        scenarios = []
        try:
            if os.path.exists(SCENARIOS_JSON):
                with open(SCENARIOS_JSON, 'r', encoding='utf-8') as f:
                    scenarios = json.load(f)
                self.logger.info(f"✅ MONITOR: Cargados {len(scenarios)} escenarios.")
        except Exception as e:
            self.logger.error(f"⚠️ MONITOR: Error cargando scenarios.json: {e}")
        return scenarios

    def monitorear(self, target_id: int, caso_n: int) -> Dict[str, Any]:
        """
        Simula la lectura de sensores y detección de contexto.
        """
        escenario_actual = next((s for s in self.scenarios if s['id'] == target_id), None)
        nombre_escenario = escenario_actual['nombre'] if escenario_actual else "Desconocido/Base"

        if escenario_actual:
            # 1. Obtener rangos del JSON
            rango_ica = escenario_actual.get('rango_ica', [0, 50])
            rango_cp = escenario_actual.get('rango_cp', [0, 100])
            rango_cola = escenario_actual.get('rango_cola_qiskit', [0, 10])
            
            # 2. Generar valores REALES (Variables Ambientales)
            ica_real = random.randint(rango_ica[0], rango_ica[1])
            cp_real = random.randint(rango_cp[0], rango_cp[1])
            cola_real_qiskit = random.randint(rango_cola[0], rango_cola[1])
            prioridad = escenario_actual.get('sla_prioridad', 'RAPIDEZ')

            # 3. Generar Perfil de Usuario
            perfiles = [
                "Turista Estándar (Solo Rutas)",
                "Grupo Deportivo (Requiere Deportes)",
                "Adulto Mayor (Requiere Entr. Tercera Edad)",
                "Familia con Niños (Requiere Entr. Familiar)",
                "Evento Nocturno (Requiere Entr. Adulto)"
            ]
            perfil_usuario = random.choice(perfiles)
            
        else:
            self.logger.warning(f"⚠️ Escenario ID {target_id} no encontrado. Usando valores base.")
            ica_real = 50; cp_real = 10; prioridad = "RAPIDEZ"; cola_real_qiskit = 5; perfil_usuario = "Estándar"

        # --- AUDITORIA ---
        self.logger.info(
            f"[CASO #{caso_n}] PARÁMETROS: "
            f"Escenario='{nombre_escenario}' | ICA={ica_real} | CP={cp_real} | "
            f"ColaQiskit={cola_real_qiskit}s | Usuario='{perfil_usuario}'"
        )
        
        return {
            "ica": ica_real,
            "complejidad_problema": cp_real,
            "prioridad": prioridad,
            "cola_qiskit": cola_real_qiskit,
            "perfil_usuario": perfil_usuario,
            "nombre_escenario": nombre_escenario
        }
