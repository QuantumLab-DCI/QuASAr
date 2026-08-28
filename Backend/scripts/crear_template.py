import os
import shutil
import importlib.util
import sys
import pandas as pd
import re

# --- Configuración ---
ORIGINAL_GRAFO_FILE = 'grafo_mc.py'
TEMP_GRAFO_FILE = 'grafo_mc_temp.py'
DATOS_CSV_PATH = 'data/datos.csv'
OLD_DATASET_PATH = 'dataset.csv' # El que subiste
NEW_DATASET_PATH = 'data/dataset.csv' # El nuevo que se creará en /data
# ---------------------

def get_feature_name(feature_string):
    """Normaliza 'Caracteristica activada' o 'Caracteristica desactivada' a 'Caracteristica'"""
    return str(feature_string).replace(" activada", "").replace(" desactivada", "")

def silenciar_y_ejecutar_grafo():
    """Copia, silencia y ejecuta grafo_mc.py para generar data/datos.csv"""
    print(f"1. Creando copia temporal: '{TEMP_GRAFO_FILE}'...")
    try:
        shutil.copyfile(ORIGINAL_GRAFO_FILE, TEMP_GRAFO_FILE)

        with open(TEMP_GRAFO_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        lines_modificadas = []
        for line in lines:
            if 'print(nodo)' in line and 'removerRelacionesInvalidas' in lines[lines.index(line)-4]:
                lines_modificadas.append('# ' + line)
            else:
                lines_modificadas.append(line)
        
        with open(TEMP_GRAFO_FILE, 'w', encoding='utf-8') as f:
            f.writelines(lines_modificadas)

        print(f"2. Importando y ejecutando módulo temporal...")
        spec = importlib.util.spec_from_file_location("grafo_mc_temp", TEMP_GRAFO_FILE)
        grafo_temp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(grafo_temp)
        
        # Asegurarse de que el directorio 'data' exista
        if not os.path.exists('data'):
            os.makedirs('data')
            
        grafo_temp.generarPosiblesEstados()
        print(f"3. ¡Éxito! '{DATOS_CSV_PATH}' ha sido generado.")
        
    except Exception as e:
        print(f"ERROR durante la ejecución de grafo_mc: {e}")
    finally:
        if os.path.exists(TEMP_GRAFO_FILE):
            os.remove(TEMP_GRAFO_FILE)
        if os.path.exists('__pycache__'):
            shutil.rmtree('__pycache__')

def crear_nuevo_dataset_mapeado():
    """
    Toma los datos etiquetados de 'dataset.csv' (antiguo) y los mapea
    a la nueva estructura de 'data/datos.csv', guardando un
    nuevo 'data/dataset.csv'
    """
    if not os.path.exists(DATOS_CSV_PATH):
        print(f"ERROR: No se encontró '{DATOS_CSV_PATH}'. Ejecute el paso 1 primero.")
        return
        
    if not os.path.exists(OLD_DATASET_PATH):
        print(f"ERROR: No se encontró '{OLD_DATASET_PATH}' en la raíz del proyecto.")
        print("Asegúrate de que el 'dataset.csv' que subiste esté en la misma carpeta que este script.")
        return

    print(f"4. Leyendo nueva estructura de '{DATOS_CSV_PATH}'...")
    
    # 1. Obtener la "plantilla" de características de la nueva estructura
    df_nuevo_template = pd.read_csv(DATOS_CSV_PATH, header=None, nrows=1)
    # Normalizamos para tener solo los nombres base: ["Visualizador...", "Turismo...", "HQC", ...]
    master_feature_list = [get_feature_name(col) for col in df_nuevo_template.iloc[0]]
    print(f"   - Nueva estructura detectada: {len(master_feature_list)} características.")

    print(f"5. Leyendo datos antiguos de '{OLD_DATASET_PATH}'...")
    
    # 2. Leer los datos etiquetados antiguos
    df_antiguo = pd.read_csv(OLD_DATASET_PATH, header=0) # Leemos con cabecera (fila 0)
    
    # Obtenemos los nombres de las características antiguas (de la cabecera)
    old_feature_list = df_antiguo.columns[:-1].tolist() # Todos menos el último ("Indice MP2.5")
    
    new_dataset_rows = []

    print(f"6. Mapeando {len(df_antiguo)} filas antiguas a la nueva estructura...")
    
    # 3. Iterar por cada fila de datos antiguos (ej. las 8 filas)
    for index, old_row in df_antiguo.iterrows():
        new_row = []
        
        # Crear un diccionario de mapeo para esta fila
        old_features_dict = {}
        for feature_name in old_feature_list:
            old_features_dict[feature_name] = old_row[feature_name]
            
        label = old_row['Indice MP2.5']

        # 4. Construir la nueva fila usando el orden de la plantilla maestra
        for feature_name in master_feature_list:
            if feature_name in old_features_dict:
                # Si la característica existía, usamos su valor (ej. "Turismo activada")
                new_row.append(old_features_dict[feature_name])
            else:
                # Si es una característica nueva (ej. "HQC"), asumimos "desactivada"
                new_row.append(f"{feature_name} desactivada")
        
        # Añadir la etiqueta al final
        new_row.append(label)
        new_dataset_rows.append(new_row)

    print(f"7. Guardando nuevo dataset en '{NEW_DATASET_PATH}'...")
    
    # 5. Guardar el nuevo dataset en la carpeta /data
    df_final = pd.DataFrame(new_dataset_rows)
    df_final.to_csv(NEW_DATASET_PATH, index=False, header=False)

    print("\n--- ¡COMPLETADO! ---")
    print(f"Se ha generado el archivo '{NEW_DATASET_PATH}'.")
    print(f"Este archivo tiene la nueva estructura ({len(master_feature_list) + 1} columnas) y {len(new_dataset_rows)} filas.")
    print("Esto solucionará el error 'Matrix size-incompatible'.")
    print("\n--- ADVERTENCIA IMPORTANTE ---")
    print("El modelo de IA ahora se entrenará solo con 8 filas de datos.")
    print("Esto NO es suficiente para un buen entrenamiento (Deep Learning).")
    print("Tu tarea manual ahora es: AÑADIR MÁS FILAS (cientos o miles) a este nuevo")
    print(f"'{NEW_DATASET_PATH}' para que el modelo pueda aprender correctamente.")

# --- Flujo de ejecución principal ---
if __name__ == "__main__":
    # Paso 1: Generar 'data/datos.csv' actualizado
    silenciar_y_ejecutar_grafo()
    
    # Paso 2: Crear 'data/dataset.csv' mapeando los datos antiguos
    crear_nuevo_dataset_mapeado()