import grafo_mc
import punto_variacion
# import aprendizaje_automatico  <--- ELIMINADO

# --- IMPORTS RESTAURADOS ---
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import time
import asyncio # Vuelve
import random  # Vuelve
import docker
# --- FIN IMPORTS ---

import os
from fastapi.responses import FileResponse, PlainTextResponse
import visualizador_grafo
from pathlib import Path
from mapek import Mapek

PROJECT_ROOT = Path(__file__).resolve().parent
os.chdir(PROJECT_ROOT)

app = FastAPI()

origins = [
    "http://oasis.ceisufro.cl"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- VARIABLES GLOBALES ---
mc = None
puntoVariacion = None
reglaAdaptacion = None

# --- TAREA PERIÓDICA RESTAURADA ---
# (No se necesitan cambios aquí, la lógica de Mapek está abstraída)
async def periodic_task():
    global puntoVariacion
    global reglaAdaptacion
    global mc
    
    # Bucle infinito que se ejecuta en segundo plano
    while True:
        print("\n" + "="*50)
        print(f"INICIANDO NUEVO CICLO DE ADAPTACIÓN (espera de 120s)")
        
        # 1. Instanciar Mapek
        mapek = Mapek()
        
        # 2. Llamar a monitoreo (que dispara el ciclo completo)
        mapek.monitoreo(mc)
        
        # 3. Actualizar el estado global para los endpoints GET
        puntoVariacion = mapek.getConocimiento()
        reglaAdaptacion = mapek.getReglaAdaptacion()
        
        # 4. Generar la visualización del estado actual en cada ciclo
        if puntoVariacion: 
            visualizador_grafo.generar_visualizacion_estado(puntoVariacion, mc, nombre_archivo='estado_actual')
        else:
            print("Ciclo omitido (posiblemente error del LLM).")

        print(f"CICLO COMPLETO. Durmiendo por 120 segundos...")
        print("="*50 + "\n")
        
        # 5. Esperar 2 minutos
        await asyncio.sleep(120)


@app.on_event("startup")
async def iniciar_app():
    global mc
    global puntoVariacion
    global reglaAdaptacion
    
    print("Iniciando aplicación...")
    # Esta línea ahora solo carga las REGLAS del modelo
    mc = grafo_mc.generarPosiblesEstados() 
    
    # --- BLOQUE DE ENTRENAMIENTO DE ML ELIMINADO ---
    # Ya no necesitamos crear el archivo 'datos_redesneuronalesprofundas.csv'
    
    # Generar la imagen del MODELO en la raíz
    try:
        visualizador_grafo.generar_visualizacion_modelo(
            mc, nombre_archivo='modelo_caracteristicas'
        )
        print("Visualización del modelo estático generada.")
    except Exception as e:
        print(f"[startup] Error al generar la visualización del modelo: {e}")
    
    # Iniciar el bucle de adaptación periódica
    print("Iniciando bucle de adaptación periódica (cada 120s)...")
    asyncio.create_task(periodic_task())
    print("Aplicación iniciada exitosamente.")


@app.get("/")
def read_root():
    return {"Hello": "World"}

# --- LOS ENDPOINTS SIGUEN SIENDO VÁLIDOS ---
# (Leen las variables globales que el bucle sigue actualizando)

@app.get("/links")
def get_links(name : str):
    if not puntoVariacion:
        return {"error": "El sistema está arrancando. Espere al primer ciclo de adaptación."}
    return puntoVariacion.obtenerConfiguracionNivel(name)

@app.get("/link")
def get_link(name : str):
    if not puntoVariacion:
        return {"error": "El sistema está arrancando. Espere al primer ciclo de adaptación."}
    return puntoVariacion.obtenerEstadoCaracteristica(name)


@app.get("/reglaAdaptacion")
def get_regla_adaptacion():
    if reglaAdaptacion is None:
         return {"regla_adaptacion_actual": "N/A (esperando primer ciclo)"}
    # Esto ahora mostrará el CONTEXTO que se envió al LLM
    return {"contexto_de_entrada": reglaAdaptacion}


@app.get("/visualizacion_modelo")
async def get_visualizacion_modelo():
    file_path = "modelo_caracteristicas.png"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Archivo no encontrado. Espera a que la app inicie completamente."}

@app.get("/visualizacion_estado")
async def get_visualizacion_estado():
    """
    Sirve la imagen que muestra el estado actual del sistema.
    Esta imagen se actualiza cada 2 minutos.
    """
    file_path = "estado_actual.png"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Archivo no encontrado. Espera a que se complete el primer ciclo de adaptación."}

@app.get("/log_cambios", response_class=PlainTextResponse)
async def get_log_cambios():
    try:
        with open("cambios.log", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "No se ha registrado ningún cambio todavía."