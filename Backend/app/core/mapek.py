from typing import Dict, List, Any, Optional
import datetime
from app.core.audit_logger import get_logger

# Importar las fases
from app.core.mapek_phases.monitor import Monitor
from app.core.mapek_phases.analyzer import Analyzer
from app.core.mapek_phases.planner import Planner
from app.core.mapek_phases.executor import Executor

class Mapek:
    """
    Motor del ciclo MAPE-K (Refactorizado - Orquestador).
    Coordina Monitor, Analyzer, Planner, Execute, Knowledge phases.
    """
    def __init__(self):
        self.logger = get_logger()
        self._mapek_trace = []
        self._caso_actual = 0
        
        # Inicializar Fases
        self.monitor_phase = Monitor()
        self.analyzer_phase = Analyzer()
        self.planner_phase = Planner()
        self.executor_phase = Executor()
        
        self._last_context = {} # Cache para getters legacy

    # --- Helper para registrar pasos en el timeline (Frontend) ---
    def _registrar_paso(self, fase, mensaje, detalles=None):
        paso = {
            "fase": fase,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "mensaje": mensaje,
            "detalles": detalles
        }
        self._mapek_trace.append(paso)
        print(f"[{fase}] {mensaje}")
    # ---------------------------------------------------------

    def ejecutar_escenario_manual(self, mc, target_id: int, caso_n: int = 0) -> None:
        """ 
        Orquesta el ciclo completo MAPE-K.
        """
        self._caso_actual = caso_n
        self._mapek_trace = [] # Limpiar traza anterior
        self._registrar_paso("INICIO", f"Iniciando ciclo MAPE-K para Escenario ID {target_id}")

        # 1. MONITOR
        contexto = self.monitor_phase.monitorear(target_id, caso_n)
        self._last_context = contexto # Guardar para getters
        
        self._registrar_paso("MONITOREO", "Sensores leídos y Perfil de usuario detectado.", {
            "ICA (Aire)": contexto['ica'],
            "Complejidad (CP)": contexto['complejidad_problema'],
            "Latencia Qiskit": f"{contexto['cola_qiskit']}s",
            "Intención Usuario": contexto['perfil_usuario']
        })

        # 2. ANALYZE
        self._registrar_paso("ANÁLISIS", "Detectada necesidad de adaptación. Consultando Agente Inteligente...", {
            "Motivo": "Cambio en contexto detectado",
            "Estrategia": "Consulta a LLM (Gemini)"
        })
        
        config_plana = self.analyzer_phase.analizar(mc, contexto, caso_n)
        
        if not config_plana:
            self._registrar_paso("ERROR", "El Agente LLM falló o la validación rechazó la configuración.")
            return

        razonamiento = self.analyzer_phase.get_razonamiento()
        self._registrar_paso("ANÁLISIS (IA)", "El Agente ha tomado una decisión.", {
            "Razonamiento": razonamiento
        })

        # 3. PLAN + KNOWLEDGE (Update)
        # La fase planner actualiza el conocimiento (PuntoVariacion) y retorna el plan ejecutable
        config_ejecutable = self.planner_phase.planificar(
            config_plana, mc, contexto['ica'], contexto['complejidad_problema']
        )
        
        activas = [k for k, v in config_ejecutable.items() if v is True]
        self._registrar_paso("PLANIFICACIÓN", "Plan de reconfiguración generado.", {
            "Estrategia": "Hot-Swap de contenedores y Backends",
            "Features a Activar": activas
        })

        # 4. EXECUTE
        self._registrar_paso("EJECUCIÓN", "Aplicando cambios en infraestructura...", {
            "Mecanismo": "Docker API + HQC Factory",
        })
        
        # Ejecutar y capturar sub-trazas (ej. HQC jobs)
        sub_trace = self.executor_phase.ejecutar(config_ejecutable, caso_n, contexto)
        
        # Integrar trazas de ejecución (si las hay)
        if sub_trace:
            for paso in sub_trace:
                self._mapek_trace.append(paso)

        self._registrar_paso("FIN", "Ciclo MAPE-K completado exitosamente.")

    # --- Getters Legacy (Mantener compatibilidad API) ---
    def getConocimiento(self):
        return self.planner_phase.get_conocimiento()

    def getReglaAdaptacion(self) -> Dict[str, Any]:
        return {
            "calidad_aire_ica": self._last_context.get('ica'),
            "complejidad_problema_cp": self._last_context.get('complejidad_problema'),
            "prioridad_sla": self._last_context.get('prioridad'),
            "razonamiento": self.analyzer_phase.get_razonamiento()
        }
    
    def getTrace(self) -> List[Dict[str, Any]]:
        return self._mapek_trace