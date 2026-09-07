import docker
from typing import Any

class DockerService:
    """Provide best-effort access to the local Docker daemon."""

    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            print(f"Docker warning: Could not connect to the Docker daemon: {e}")
            self.client = None

    def list_containers(self, all=True):
        """Return containers, or an empty list when Docker is unavailable."""
        if not self.client:
            return []
        try:
            return self.client.containers.list(all=all)
        except Exception:
            return []

    def get_container(self, container_id_or_name: str):
        """Return a container by ID or name when available."""
        if not self.client:
            return None
        try:
            return self.client.containers.get(container_id_or_name)
        except docker.errors.NotFound:
            return None

    def get_container_logs(self, container_name: str, tail: int = 50) -> dict[str, Any]:
        """Return recent output from the named container."""
        if not self.client:
             return {"status": "error", "logs": "Docker client not initialized."}
        
        name_clean = container_name.lower().replace(" ", "_").strip()
        if "hybrid_quantum" in name_clean:
            name_clean = "hybrid_quantum_computing"
        if "air_quality" in name_clean:
            name_clean = "air_quality_manager"
        
        try:
            container = self.client.containers.get(name_clean)
            logs_raw = container.logs(tail=tail).decode('utf-8')
            return {"status": "ok", "logs": logs_raw}
        except docker.errors.NotFound:
            return {"status": "error", "logs": f"Container '{name_clean}' not found or stopped."}
        except Exception as e:
            return {"status": "error", "logs": f"Error reading Docker API: {str(e)}"}

    def start_container(self, container) -> bool:
        try:
            container.start()
            return True
        except Exception as e:
            print(f"Error starting container {container.name}: {e}")
            return False

    def stop_container(self, container) -> bool:
        try:
            container.stop()
            return True
        except Exception as e:
            print(f"Error stopping container {container.name}: {e}")
            return False
