from abc import ABC, abstractmethod

class QuantumBackend(ABC):
    """Define the contract for quantum backend adapters."""

    @abstractmethod
    def execute_job(self, algorithm_id: str, parameters: dict) -> dict:
        """Execute an algorithm and return its backend-specific result."""
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}>"
