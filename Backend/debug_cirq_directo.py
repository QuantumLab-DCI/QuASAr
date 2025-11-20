import sys
import os

# 1. Configurar el Path para encontrar los módulos de 'app'
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from app.services.hqc_backends.cirq_adapter import CirqAdapter
except ImportError as e:
    print(f"❌ Error de importación crítico: {e}")
    print("Asegúrate de estar en el entorno virtual correcto con cirq y tensorflow-quantum instalados.")
    sys.exit(1)

def test_cirq_force():
    print("\n🚀 INICIANDO PRUEBA FORZADA DE CIRQ ADAPTER (TFQ)")
    print("===================================================")

    # 2. Instanciar el adaptador
    try:
        adapter = CirqAdapter()
        print("✅ Adaptador Cirq instanciado correctamente.")
    except Exception as e:
        print(f"❌ Fallo al instanciar adaptador: {e}")
        return

    # 3. Definir parámetros de prueba
    # Usamos 3 nodos y profundidad 1 para una prueba rápida.
    # Puedes subir 'size' a 4 para probar carga media.
    params_simulados = {
        "problema_id": "debug_cirq_manual_001",
        "size": 3,       # 3 Nodos (Max-Cut en triángulo)
        "depth": 1       # 1 Capa de QAOA/VQE
    }
    
    # Probamos QAOA (puedes cambiar a "VQE" si prefieres)
    algoritmo = "QAOA"

    print(f"⚙️  Parámetros: {params_simulados}")
    print(f"⚙️  Algoritmo: {algoritmo}")
    print("---------------------------------------------------")

    # 4. Ejecutar el trabajo directamente
    try:
        print("⏳ Ejecutando simulación en TensorFlow Quantum...")
        resultado = adapter.execute_job(algoritmo, params_simulados)
        
        print("\n✅ EJECUCIÓN EXITOSA")
        print("====================")
        print(f"Backend: {resultado.get('backend')}")
        print(f"Costo Óptimo (Energía): {resultado.get('costo_optimo')}")
        print(f"Parámetros Optimizados: {resultado.get('parametros_optimos')}")
        
        evidencia = resultado.get('evidencia_visual')
        print(f"Evidencia visual: {evidencia}")
        
        # Verificación extra de archivo
        if evidencia and "No generado" not in evidencia:
            # Convertir ruta relativa de API a ruta absoluta de sistema para verificar
            ruta_real = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', os.path.basename(evidencia)))
            if os.path.exists(ruta_real):
                print(f"📂 Archivo verificado en disco: {ruta_real}")
            else:
                print(f"⚠️ El archivo {evidencia} no se encuentra en la ruta esperada.")
        
    except Exception as e:
        print("\n❌ EJECUCIÓN FALLIDA (Capturada en script)")
        print("==========================================")
        print(f"Tipo de Error: {type(e).__name__}")
        print(f"Mensaje: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cirq_force()