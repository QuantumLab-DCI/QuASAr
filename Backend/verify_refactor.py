import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

print("🔍 Verifying Backend Refactoring...")

try:
    print("1. Testing Imports...")
    from app import create_app
    from app.core.state import state_manager
    from app.services.docker_service import DockerService
    from app.services.file_service import FileService
    from app.api import dashboard_bp, control_bp, legacy_bp
    
    # New Modular Imports
    from app.core.mapek import Mapek
    from app.core.mapek_phases.monitor import Monitor
    from app.core.mapek_phases.analyzer import Analyzer
    from app.core.mapek_phases.planner import Planner
    from app.core.mapek_phases.executor import Executor
    
    print("   ✅ Imports successful (Services & Modules).")

    print("2. Testing App Factory & Mapek Initialization...")
    try:
        app, mc = create_app()
        print("   ✅ App created successfully.")
        
        # Test Mapek Instantiation
        mapek = Mapek()
        print(f"   ✅ Mapek Initialized with phases: "
              f"{mapek.monitor_phase.__class__.__name__}, "
              f"{mapek.analyzer_phase.__class__.__name__}, "
              f"{mapek.planner_phase.__class__.__name__}, "
              f"{mapek.executor_phase.__class__.__name__}")
              
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        sys.exit(1)

    print("3. Testing Blueprint Registration...")
    rules = [str(r) for r in app.url_map.iter_rules()]
    
    expected_routes = [
        '/api/estado',
        '/api/escenarios',
        '/api/seleccionar_escenario',
        '/api/logs',
        '/api/links/<name>'
    ]
    
    for route in expected_routes:
        found = any(route in r for r in rules)
        status = "✅" if found else "❌"
        print(f"   {status} Route found: {route}")

    print("\n🎉 Verification Complete! The refactoring seems successful.")

except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
    sys.exit(1)
