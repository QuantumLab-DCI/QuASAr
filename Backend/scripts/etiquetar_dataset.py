import csv
import random

# --- DEFINE LABELING RULES HERE ---
# This logic should reflect the system's decision-making process.
def asignar_regla(fila_caracteristicas):
    
    # RULE 1: HQC logic (the most important rule)
    # Use column 10 as the index of "HQC activada" (adjust if necessary)
    # A more robust approach is to search for the string:
    
    if "HQC activada" in fila_caracteristicas:
        # If HQC is active, this is a HIGH-complexity problem.
        # Assign a random value in the high range.
        return random.randint(300, 350)
    
    else:
        # --- CLASSICAL CASE (Without HQC) ---
        # This can be as simple or complex as needed.
        
        # Simple strategy:
        # return random.randint(1, 299)
        
        # "Smarter" strategy (optional but recommended):
        # Assign complexity based on the number of active classical features.
        score = 0
        if "Deportes activada" in fila_caracteristicas:
            score += 80
        if "Entretenimiento activada" in fila_caracteristicas:
            score += 60
        if "Turismo activada" in fila_caracteristicas:
            score += 40
        if "Visualizador restriccion uso lena activada" in fila_caracteristicas:
            score += 50
            
        # Ensure that the base score is at least 1 and does not exceed the threshold
        if score == 0:
            return random.randint(1, 20) # Very basic configuration
        else:
            # Normalize the score to remain below the threshold of 300
            # For example, if the maximum score is 230 (80+60+40+50), add some noise
            return min(score + random.randint(1, 50), 299)


# --- MAIN FILE-PROCESSING SCRIPT ---
def procesar_csv():
    archivo_entrada = 'data/datos.csv' # Read the clean permutations
    archivo_salida = 'data/dataset.csv' # Write the training dataset
    
    filas_nuevas = []
    
    print(f"Abriendo {archivo_entrada} para generar {archivo_salida}...")
    
    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f_in:
            reader = csv.reader(f_in)
            
            # Read all rows
            filas_originales = list(reader)
            
            # If `datos.csv` has a header, skip or process it
            # Assume for now that it has no header.
            
            for fila in filas_originales:
                if not fila: # Skip empty rows
                    continue
                    
                # 1. Assign the adaptation rule
                regla = asignar_regla(fila)
                
                # 2. Create the new row (features + rule)
                nueva_fila = fila + [regla]
                filas_nuevas.append(nueva_fila)

        print(f"Se procesaron {len(filas_nuevas)} filas.")
        
        # 3. Write the new dataset.csv file
        with open(archivo_salida, 'w', newline='', encoding='utf-8') as f_out:
            writer = csv.writer(f_out)
            
            # Optionally write a header
            # num_features = len(filas_nuevas[0]) - 1
            # header = [f"feature_{i}" for i in range(num_features)] + ["regla_adaptacion"]
            # writer.writerow(header)
            
            writer.writerows(filas_nuevas)
            
        print(f"¡Éxito! Archivo {archivo_salida} generado con reglas de adaptación correctas.")

    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo {archivo_entrada}.")
        print("Asegúrate de haber ejecutado 'python grafo_mc.py' primero.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")

# --- Run the Script ---
if __name__ == "__main__":
    procesar_csv()
