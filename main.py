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
        #agregar regla adaptacion
        mapek = Mapek()
        mapek.monitoreo(mc)
        puntoVariacion = mapek.getConocimiento()
        reglaAdaptacion = mapek.getReglaAdaptacion()
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




