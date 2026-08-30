# app/services/hqc_backends/base_backend.py
from abc import ABC, abstractmethod

class QuantumBackend(ABC):
    """
    Abstract base class (interface) for all quantum backend adapters.
    Define a common contract that all supported backends must follow.
    """

    @abstractmethod
    def execute_job(self, algorithm_id: str, parameters: dict) -> dict:
        """
        Execute a quantum job for a given algorithm and parameters.
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}>"
