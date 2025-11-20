# debug_qiskit_directo.py
import sys
import os

# Aseguramos que Python encuentre los módulos de 'app'
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from app.services.hqc_backends.qiskit_adapter import QiskitAdapter
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    sys.exit(1)

def test_qiskit_force():
    print("\n🚀 INICIANDO PRUEBA FORZADA DE QISKIT ADAPTER")
    print("===============================================")

    # 1. Instanciar el adaptador
    try:
        adapter = QiskitAdapter()
        print("✅ Adaptador instanciado correctamente.")
    except Exception as e:
        print(f"❌ Fallo al instanciar adaptador: {e}")
        return

    # 2. Definir los parámetros que causan el error (Alta complejidad)
    # Según tus logs: TSP 5 ciudades, Profundidad 2
    params_simulados = {
        "problema_id": "debug_manual_001",
        "complejidad_cp": 100, # Complejidad media
        "size": 4,             # <--- CAMBIO: 3 Ciudades (9 Qubits = Muy rápido)
        "depth": 2             # <--- CAMBIO: Profundidad 1 (Circuito más corto)
    }
    
    algoritmo = "QAOA"

    print(f"⚙️  Parámetros: {params_simulados}")
    print(f"⚙️  Algoritmo: {algoritmo}")
    print("-----------------------------------------------")

    # 3. Ejecutar el trabajo directamente
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