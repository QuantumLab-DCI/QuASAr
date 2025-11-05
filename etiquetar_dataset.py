import csv
import random

# --- DEFINE TUS REGLAS DE ETIQUETADO AQUÍ ---
# Esta lógica debe reflejar el "cerebro" de tu sistema.
def asignar_regla(fila_caracteristicas):
    
    # REGLA 1: Lógica HQC (La más importante)
    # Usamos la columna 10 como índice de "HQC activada" (ajusta si es necesario)
    # Una forma más robusta es buscar por el string:
    
    if "HQC activada" in fila_caracteristicas:
        # Si HQC está activo, es un problema de ALTA complejidad.
        # Asignamos un valor aleatorio en el rango alto.
        return random.randint(300, 350)
    
    else:
        # --- CASO CLÁSICO (Sin HQC) ---
        # Aquí puedes ser tan simple o complejo como quieras.
        
        # Estrategia Simple:
        # return random.randint(1, 299)
        
        # Estrategia "Más Inteligente" (Opcional, pero recomendada):
        # Asigna complejidad basada en cuántas features clásicas están activas.
        score = 0
        if "Deportes activada" in fila_caracteristicas:
            score += 80
        if "Entretenimiento activada" in fila_caracteristicas:
            score += 60
        if "Turismo activada" in fila_caracteristicas:
            score += 40
        if "Visualizador restriccion uso lena activada" in fila_caracteristicas:
            score += 50
            
        # Aseguramos que el score base sea al menos 1 y no pase del umbral
        if score == 0:
            return random.randint(1, 20) # Configuración muy básica
        else:
            # Normaliza el score para que quepa bajo el umbral de 300
            # ej. si tu score max es 230 (80+60+40+50), suma un poco de ruido
            return min(score + random.randint(1, 50), 299)


# --- SCRIPT PRINCIPAL PARA PROCESAR EL ARCHIVO ---
def procesar_csv():
    archivo_entrada = 'data/datos.csv' # Leemos las permutaciones limpias
    archivo_salida = 'data/dataset.csv' # Escribimos el dataset de entrenamiento
    
    filas_nuevas = []
    
    print(f"Abriendo {archivo_entrada} para generar {archivo_salida}...")
    
    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f_in:
            reader = csv.reader(f_in)
            
            # Leemos todas las filas
            filas_originales = list(reader)
            
            # Si `datos.csv` tiene un encabezado, lo saltamos o procesamos
            # Asumamos que no tiene encabezado por ahora.
            
            for fila in filas_originales:
                if not fila: # Omitir filas vacías
                    continue
                    
                # 1. Asignar la regla de adaptación
                regla = asignar_regla(fila)
                
                # 2. Crear la nueva fila (features + regla)
                nueva_fila = fila + [regla]
                filas_nuevas.append(nueva_fila)

        print(f"Se procesaron {len(filas_nuevas)} filas.")
        
        # 3. Escribir el nuevo archivo dataset.csv
        with open(archivo_salida, 'w', newline='', encoding='utf-8') as f_out:
            writer = csv.writer(f_out)
            
            # (Opcional) Escribir un encabezado
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

# --- Ejecutar el script ---
if __name__ == "__main__":
    procesar_csv()