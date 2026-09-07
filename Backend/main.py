"""Legacy-compatible entry point for the active English backend."""

from app import create_app, setup_startup_tasks
from app.config import DEFAULT_HOST, DEFAULT_PORT


app, feature_model = create_app()


if __name__ == "__main__":
    print("Starting the Flask application.")
    setup_startup_tasks(feature_model)
    app.run(host=DEFAULT_HOST, port=DEFAULT_PORT, debug=False)
