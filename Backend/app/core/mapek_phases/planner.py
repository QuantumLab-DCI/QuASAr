from typing import Dict, Any, List
from app.core import punto_variacion
from app.core.audit_logger import get_logger

class Planner:
    """
    Phase 3: PLAN
    Generate the reconfiguration plan (deltas) based on the LLM analysis.
    """
    def __init__(self):
        self.logger = get_logger()
        self._puntoVariacion = None

    def planificar(self, configuracion_llm: Dict[str, bool], mc, ica: int, complejidad_problema: int) -> Dict[str, Any]:
        """
        - Update the Variation Point with the new configuration.
        - Generate the flat configuration dictionary for the Executor.
        """
        # Convert the flat Boolean dictionary to a list of propositions such as
        # ["FeatA activada", ...]. This is required by the current PuntoVariacion class.
        configuracion_formal = []
        for key, value in configuracion_llm.items(): 
            # Find the formal name in the feature model
            nombre_formal = next(
                (c.getNombre for c in mc.caracteristicas 
                    if c.getNombre.replace(" ", "_").lower() == key.lower()), 
                key.replace("_", " ").capitalize()
            )
            estado = "activada" if value else "desactivada"
            configuracion_formal.append(f"{nombre_formal} {estado}")

        self.logger.info("KNOWLEDGE: Actualizando base de conocimiento y estado global.")
        
        # Update the configuration management object
        self._puntoVariacion = punto_variacion.PuntoVariacion(configuracion_formal, mc, "gestor_aire")
        
        # Obtain the clean {feature: bool} dictionary for execution
        config_ejecutable = self._puntoVariacion.obtenerConfiguracion()
        
        return config_ejecutable
    
    def get_conocimiento(self):
        """Return the most recently managed variation point."""
        return self._puntoVariacion
