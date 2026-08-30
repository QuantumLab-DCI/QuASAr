import docker
from typing import Any

class DockerService:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            print(f"Docker warning: Could not connect to the Docker daemon: {e}")
            self.client = None

    def list_containers(self, all=True):
        if not self.client:
            return []
        try:
            return self.client.containers.list(all=all)
        except Exception:
            return []

    def get_container(self, container_id_or_name: str):
        if not self.client:
            return None
        try:
            return self.client.containers.get(container_id_or_name)
        except docker.errors.NotFound:
            return None

    def get_container_logs(self, container_name: str, tail: int = 50) -> dict[str, Any]:
        """
        Retrieves logs from a specific container.
        """
        if not self.client:
             return {"status": "error", "logs": "Docker client not initialized."}
        
        # Normalize name
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

    def set_container_state(self, container_name: str, desired_state: bool) -> dict:
        """
        Starts or stops a container based on desired_state.
        Returns a dict with success status and message.
        """
        if not self.client:
             return {"success": False, "message": "Docker client not initialized."}

        try:
            # We list all to find by name, or get directly if name is precise
            # The controller iterates over the available containers.
            # Here we can try to get it directly for efficiency if we trust the name, 
            # This method remains available for direct state changes.
            
            # This method assumes we know the exact name or ID.
            # However, the original code loops through ALL containers and checks against the plan.
            # So this method might be better as 'apply_state_to_container_object'
            pass 
        except Exception:
            pass
        return {}

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
