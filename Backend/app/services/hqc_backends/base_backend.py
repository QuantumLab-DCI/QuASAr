# app/services/hqc_backends/base_backend.py
from abc import ABC, abstractmethod

class QuantumBackend(ABC):
    """
    Abstract base class (interface) for all quantum backend adapters.
    Define a common contract that all backends (Qiskit, SpinQ, TQL) must follow.
    """

    @abstractmethod
    def execute_job(self, algoritmo: str, params: dict) -> dict:
        """
        Execute a quantum job for a given algorithm and parameters.
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}>"
