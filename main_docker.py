import grafo_mc
import punto_variacion
import aprendizaje_automatico
import docker
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import time
import asyncio
import random


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
    global numRandom
    numRandom = random.randint(1, 350)
    configuracion = aprendizaje_automatico.arbolesAleatoriosInverso("data/datos_redesneuronales.csv", numRandom)
    puntoVariacion = punto_variacion.PuntoVariacion(configuracion, mc, "Gestor Aire")
    contenedores=puntoVariacion.obtenerConfiguracion()
    print("pasaron 2 minutos")
    for container in client.containers.list(all=True):
        if(container.name in contenedores):
            cont=client.containers.get(container.id)
            if(contenedores[container.name]==True and cont.status=="exited"):
                cont.start()
                print(f"contenedor {container.name} iniciado")
            elif(contenedores[container.name]==False and cont.status=="running"):
                cont.stop()
                print(f"contenedor {container.name} detenido")
    asyncio.create_task(asyncio.sleep(120))

@app.on_event("startup")
async def iniciar_app():
    global mc
    global puntoVariacion
    global client
    mc = grafo_mc.generarPosiblesEstados()
    aprendizaje_automatico.guardarPredicciones(aprendizaje_automatico.redesNeuronales("data/dataset.csv", "data/datos.csv"),
                                               "data/datos_redesneuronales.csv")
    client = docker.from_env()
    asyncio.create_task(periodic_task())

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/links")
def get_links(name : str):
    name = name.replace("_", " ")
    return puntoVariacion.obtenerConfiguracionNivel(name)

@app.get("/link")
def get_link(name : str):
    name = name.replace("_", " ")
    return puntoVariacion.obtenerEstadoCaracteristica(name)


@app.get("/reglaAdaptacion")
def get_regla_adaptacion():
    return numRandom



