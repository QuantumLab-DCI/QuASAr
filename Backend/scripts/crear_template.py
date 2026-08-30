import os
import shutil
import importlib.util
import sys
import pandas as pd
import re

# --- Configuration ---
ORIGINAL_GRAFO_FILE = 'grafo_mc.py'
TEMP_GRAFO_FILE = 'grafo_mc_temp.py'
DATOS_CSV_PATH = 'data/datos.csv'
OLD_DATASET_PATH = 'dataset.csv' # Previously uploaded file
NEW_DATASET_PATH = 'data/dataset.csv' # New file to be created in /data
# ---------------------

def get_feature_name(feature_string):
    """Normalize 'Caracteristica activada' or 'Caracteristica desactivada' to 'Caracteristica'."""
    return str(feature_string).replace(" activada", "").replace(" desactivada", "")

def silenciar_y_ejecutar_grafo():
    """Copy grafo_mc.py, suppress its output, and execute it to generate data/datos.csv."""
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
        
        # Ensure that the 'data' directory exists
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
    Take labeled data from the old 'dataset.csv', map it to the new
    'data/datos.csv' structure, and save a new 'data/dataset.csv'.
    """
    if not os.path.exists(DATOS_CSV_PATH):
        print(f"ERROR: No se encontró '{DATOS_CSV_PATH}'. Ejecute el paso 1 primero.")
        return
        
    if not os.path.exists(OLD_DATASET_PATH):
        print(f"ERROR: No se encontró '{OLD_DATASET_PATH}' en la raíz del proyecto.")
        print("Asegúrate de que el 'dataset.csv' que subiste esté en la misma carpeta que este script.")
        return

    print(f"4. Leyendo nueva estructura de '{DATOS_CSV_PATH}'...")
    
    # 1. Get the feature template from the new structure
    df_nuevo_template = pd.read_csv(DATOS_CSV_PATH, header=None, nrows=1)
    # Normalize the values to retain only base names: ["Visualizador...", "Turismo...", "HQC", ...]
    master_feature_list = [get_feature_name(col) for col in df_nuevo_template.iloc[0]]
    print(f"   - Nueva estructura detectada: {len(master_feature_list)} características.")

    print(f"5. Leyendo datos antiguos de '{OLD_DATASET_PATH}'...")
    
    # 2. Read the old labeled data
    df_antiguo = pd.read_csv(OLD_DATASET_PATH, header=0) # Read with a header (row 0)
    
    # Get the old feature names from the header
    old_feature_list = df_antiguo.columns[:-1].tolist() # All except the last one ("Indice MP2.5")
    
    new_dataset_rows = []

    print(f"6. Mapeando {len(df_antiguo)} filas antiguas a la nueva estructura...")
    
    # 3. Iterate over each old data row (for example, the 8 rows)
    for index, old_row in df_antiguo.iterrows():
        new_row = []
        
        # Create a mapping dictionary for this row
        old_features_dict = {}
        for feature_name in old_feature_list:
            old_features_dict[feature_name] = old_row[feature_name]
            
        label = old_row['Indice MP2.5']

        # 4. Build the new row using the master template order
        for feature_name in master_feature_list:
            if feature_name in old_features_dict:
                # If the feature existed, use its value (for example, "Turismo activada")
                new_row.append(old_features_dict[feature_name])
            else:
                # If this is a new feature (for example, "HQC"), assume "desactivada"
                new_row.append(f"{feature_name} desactivada")
        
        # Append the label
        new_row.append(label)
        new_dataset_rows.append(new_row)

    print(f"7. Guardando nuevo dataset en '{NEW_DATASET_PATH}'...")
    
    # 5. Save the new dataset in the /data directory
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

# --- Main Execution Flow ---
if __name__ == "__main__":
    # Step 1: Generate an updated 'data/datos.csv'
    silenciar_y_ejecutar_grafo()
    
    # Step 2: Create 'data/dataset.csv' by mapping the old data
    crear_nuevo_dataset_mapeado()
