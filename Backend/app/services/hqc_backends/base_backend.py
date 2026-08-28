# app/services/hqc_backends/base_backend.py
from abc import ABC, abstractmethod

class QuantumBackend(ABC):
    """
    Clase base abstracta (Interfaz) para todos los adaptadores de backend cuántico.
    Define un contrato común que todos los backends (Qiskit, SpinQ, TQL) deben seguir.
    """

    @abstractmethod
    def execute_job(self, algoritmo: str, params: dict) -> dict:
        """
        Ejecuta un trabajo cuántico dado un algoritmo y parámetros.
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}>"