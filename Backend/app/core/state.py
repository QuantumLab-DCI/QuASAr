from threading import Lock
from typing import Optional, List, Dict, Any

class StateManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(StateManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        
        # --- Global State Variables ---
        self.mc = None  # Feature Model
        self.pv = None  # Variation Point (Configuration)
        self.regla_adaptacion = None
        self.trace: List[Dict[str, Any]] = [] # MAPE-K Cycle Trace
        
        # --- Control Variables ---
        self.escenario_activo_id = 1
        self.en_ejecucion = False
        self.execution_counter = 0

    def get_mc(self):
        return self.mc

    def set_mc(self, mc):
        self.mc = mc

    def get_pv(self):
        return self.pv

    def set_pv(self, pv):
        self.pv = pv

    def get_regla_adaptacion(self):
        return self.regla_adaptacion

    def set_regla_adaptacion(self, regla):
        self.regla_adaptacion = regla

    def get_trace(self):
        return self.trace

    def set_trace(self, trace):
        self.trace = trace

    def get_escenario_id(self):
        return self.escenario_activo_id

    def set_escenario_id(self, id: int):
        self.escenario_activo_id = id

    def is_running(self):
        return self.en_ejecucion

    def set_running(self, running: bool):
        self.en_ejecucion = running

    def increment_counter(self):
        self.execution_counter += 1
        return self.execution_counter
    
    def get_counter(self):
        return self.execution_counter

# Singleton Accessor
state_manager = StateManager()
