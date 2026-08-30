import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

print("Verifying the active backend architecture...")

try:
    print("1. Testing imports...")
    from app import create_app
    from app.adaptation_task import run_on_demand_adaptation_cycle
    from app.core.feature_model import FeatureModel, build_air_quality_feature_model
    from app.core.knowledge import KnowledgeBase, knowledge_base
    from app.core.mapek_controller import MAPEKController
    from app.core.variation_point import VariationPoint
    from app.services.docker_service import DockerService
    from app.services.file_service import FileService
    from app.api import dashboard_bp, control_bp, legacy_bp

    from app.core.mapek_phases.monitor import Monitor
    from app.core.mapek_phases.analyzer import Analyzer
    from app.core.mapek_phases.planner import Planner
    from app.core.mapek_phases.executor import Executor

    print("   Imports succeeded for services, MAPE-K phases, and domain classes.")

    print("2. Testing the application factory and MAPE-K initialization...")
    try:
        app, feature_model = create_app()
        print("   Application created successfully.")

        controller = MAPEKController()
        print(f"   MAPEKController initialized with phases: "
              f"{controller.monitor_phase.__class__.__name__}, "
              f"{controller.analyzer_phase.__class__.__name__}, "
              f"{controller.planner_phase.__class__.__name__}, "
              f"{controller.executor_phase.__class__.__name__}")

    except Exception as error:
        print(f"   Initialization failed: {error}")
        sys.exit(1)

    print("3. Testing blueprint registration...")
    rules = [str(rule) for rule in app.url_map.iter_rules()]

    expected_routes = [
        '/api/state',
        '/api/scenarios',
        '/api/select-scenario',
        '/api/logs',
        '/api/links/<string:name>',
        '/api/adaptation-rule',
    ]

    for route in expected_routes:
        found = any(route in rule for rule in rules)
        status = "FOUND" if found else "MISSING"
        print(f"   {status} Route found: {route}")

    if not all(any(route in rule for rule in rules) for route in expected_routes):
        raise RuntimeError("One or more required routes are missing.")
    print("\nBackend verification completed successfully.")

except ImportError as error:
    print(f"Import error: {error}")
    sys.exit(1)
except Exception as error:
    print(f"Unexpected error: {error}")
    sys.exit(1)
