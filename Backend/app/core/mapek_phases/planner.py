from typing import Dict, Any, List
from app.core import punto_variacion
from app.core.audit_logger import get_logger

class Planner:
    """
    Fase 3: PLAN
    Responsable de generar el plan de reconfiguración (deltas) basado en el análisis del LLM.
    """
    def __init__(self):
        self.logger = get_logger()
        self._puntoVariacion = None

    def planificar(self, configuracion_llm: Dict[str, bool], mc, ica: int, complejidad_problema: int) -> Dict[str, Any]:
        """
        - Actualiza el Punto de Variación con la nueva configuración.
        - Genera el diccionario de configuración plana para el Executor.
        """
        # Convertir diccionario plano booleano a lista de proposiciones ["FeatA activada", ...]
        # Esto es necesario para la clase PuntoVariacion actual (legacy logic)
        configuracion_formal = []
        for key, value in configuracion_llm.items(): 
            # Buscar nombre formal en el MC
            nombre_formal = next(
                (c.getNombre for c in mc.caracteristicas 
                    if c.getNombre.replace(" ", "_").lower() == key.lower()), 
                key.replace("_", " ").capitalize()
            )
            estado = "activada" if value else "desactivada"
            configuracion_formal.append(f"{nombre_formal} {estado}")

        self.logger.info("KNOWLEDGE: Actualizando base de conocimiento y estado global.")
        
        # Actualizamos el objeto de gestión de configuración
        self._puntoVariacion = punto_variacion.PuntoVariacion(configuracion_formal, mc, "gestor_aire")
        
        # Obtenemos el diccionario limpio de {feature: bool} para ejecución
        config_ejecutable = self._puntoVariacion.obtenerConfiguracion()
        
        return config_ejecutable
    
    def get_conocimiento(self):
        """Devuelve el último punto de variación gestionado."""
        return self._puntoVariacion
