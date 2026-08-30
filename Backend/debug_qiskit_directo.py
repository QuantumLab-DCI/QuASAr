# debug_qiskit_directo.py
import sys
import os

# Ensure Python can find the 'app' modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from app.services.hqc_backends.qiskit_adapter import QiskitAdapter
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    sys.exit(1)

def test_qiskit_force():
    print("\n🚀 INICIANDO PRUEBA FORZADA DE QISKIT ADAPTER")
    print("===============================================")

    # 1. Instantiate the adapter
    try:
        adapter = QiskitAdapter()
        print("✅ Adaptador instanciado correctamente.")
    except Exception as e:
        print(f"❌ Fallo al instanciar adaptador: {e}")
        return

    # 2. Define the parameters that cause the error (high complexity)
    # According to the logs: 5-city TSP, depth 2
    params_simulados = {
        "problema_id": "debug_manual_001",
        "complejidad_cp": 100, # Medium complexity
        "size": 3,             # <--- CHANGE: 3 cities (9 qubits = very fast)
        "depth": 1             # <--- CHANGE: Depth 1 (shorter circuit)
    }
    
    algoritmo = "QAOA"

    print(f"⚙️  Parámetros: {params_simulados}")
    print(f"⚙️  Algoritmo: {algoritmo}")
    print("-----------------------------------------------")

    # 3. Execute the job directly
    try:
        resultado = adapter.execute_job(algoritmo, params_simulados)
        
        print("\n✅ EJECUCIÓN EXITOSA")
        print("====================")
        print(f"Costo Óptimo: {resultado.get('costo_optimo')}")
        print(f"Ruta (Variables): {resultado.get('variables_activas')}")
        print(f"Evidencia guardada en: {resultado.get('evidencia_visual')}")
        
    except Exception as e:
        print("\n❌ EJECUCIÓN FALLIDA (Capturada en script)")
        print("==========================================")
        print(f"Tipo de Error: {type(e).__name__}")
        print(f"Mensaje: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_qiskit_force()
