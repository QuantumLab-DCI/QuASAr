from docker import client

import grafo_mc
import punto_variacion
import aprendizaje_automatico

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import time
import asyncio
import random
import docker
import os # <-- AÑADIR
from fastapi.responses import FileResponse, PlainTextResponse # <-- AÑADIR
import visualizador_grafo # <-- AÑADIR NUESTRO MÓDULO

from mapek import Mapek

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
async def periodic_task():
    global puntoVariacion
    global reglaAdaptacion
    while True:
        # ... (código existente del ciclo mapek) ...
        mapek = Mapek()
        mapek.monitoreo(mc)
        puntoVariacion = mapek.getConocimiento()
        reglaAdaptacion = mapek.getReglaAdaptacion()
        
        # Generar la visualización del estado actual en cada ciclo
        if puntoVariacion: # <-- AÑADIR (asegurarse de que no sea nulo)
            visualizador_grafo.generar_visualizacion_estado(puntoVariacion, mc, nombre_archivo='estado_actual')

        print("pasaron 2 minutos")
        await asyncio.sleep(120)


@app.on_event("startup")
async def iniciar_app():
    global mc
    global puntoVariacion
    mc = grafo_mc.generarPosiblesEstados()
    #aprendizaje_automatico.guardarPredicciones(aprendizaje_automatico.predecirResultadoRedesNeuronales(aprendizaje_automatico.entrenarRedesNeuronales("data/dataset.csv"),"data/datos.csv"),"data/datos_redesneuronales.csv")
    aprendizaje_automatico.guardarPredicciones(aprendizaje_automatico.entrenamientoPorEtapas(),"data/datos_redesneuronalesprofundas.csv")
    asyncio.create_task(periodic_task())

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/links")
def get_links(name : str):
    return puntoVariacion.obtenerConfiguracionNivel(name)

@app.get("/link")
def get_link(name : str):
    return puntoVariacion.obtenerEstadoCaracteristica(name)


@app.get("/reglaAdaptacion")
def get_regla_adaptacion():
    return reglaAdaptacion

# --- AÑADIR ESTOS NUEVOS ENDPOINTS AL FINAL DEL ARCHIVO ---

@app.get("/visualizacion_modelo")
async def get_visualizacion_modelo():
    """
    Sirve la imagen estática del modelo de características.
    """
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
    """
    Muestra un log de texto con el historial de cambios registrados.
    """
    try:
        with open("cambios.log", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "No se ha registrado ningún cambio todavía."




