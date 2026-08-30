from fastapi import FastAPI
import grafo_mc
import aprendizaje_automatico
import json

import punto_variacion

app = FastAPI()

@app.on_event("startup")
async def iniciar_app():
    global mc
    global puntoVariacion
    mc = grafo_mc.generarPosiblesEstados()
    aprendizaje_automatico.guardarPredicciones(aprendizaje_automatico.redesNeuronales("data/dataset.csv", "data/datos.csv"),
                                               "data/datos_redesneuronales.csv")


@app.get("/obtenerReconfiguracion")
async def obtenerReconfiguracion(reglaAdaptacion1 : float):
    puntoVariacion1 = aprendizaje_automatico.arbolesAleatoriosInverso("data/datos_redesneuronales.csv", 1)
    return puntoVariacion1

@app.get("/obtenerReconfiguracionJSON")
async def obtenerReconfiguracionJSON(reglaAdaptacion1 : float):
    puntoVariacion1 = aprendizaje_automatico.obtenerJSONPrediccion(aprendizaje_automatico.arbolesAleatoriosInverso("data/datos_redesneuronales.csv", reglaAdaptacion1))
    return puntoVariacion1


# Function that returns the complete feature tree
@app.get("/obtenerArbol")
async def obtenerCaracteristicas():
    return mc.obtenerArbol()

# Function that returns the relationships of a feature
@app.get("/obtenerRelacionesCaracteristica")
async def obtenerRelacionesCaracteristica(caracteristica : str):
    return mc.obtenerRelacionesCaracteristica(caracteristica)

# Function that returns all relationships in the feature model
@app.get("/obtenerRelacionesMC")
async def obtenerRelacionesMC():
    return mc.obtenerRelacionesMC()

def inicializar():
    # Generate the graph to permute all possible model states
    mc = grafo_mc.generarPosiblesEstados()
    # Associate an adaptation rule with each variation point created in the permutation
    aprendizaje_automatico.guardarPredicciones(
        aprendizaje_automatico.redesNeuronales("data/dataset.csv", "data/datos.csv"),
        "data/datos_redesneuronales.csv")

    # Create an adaptation rule; ideally it should be a random number
    reglaAdaptacion1 = 250.2
    # Return a random number that simulates an adaptation rule and classifies a variation point
    # This classification uses the random forest classification algorithm
    puntoVariacion1 = aprendizaje_automatico.arbolesAleatoriosInverso("data/datos_redesneuronales.csv", reglaAdaptacion1)
    # Present variation point 1
    print("Punto de variación 1, ", puntoVariacion1)

    objetoPuntoVariacion = punto_variacion.PuntoVariacion(puntoVariacion1,mc)
    print("JSON con configuracion ", objetoPuntoVariacion.obtenerConfiguracion())
    print("Caracteristicas activas del sub nivel Turismo ",objetoPuntoVariacion.obtenerConfiguracionNivel("Turismo"))
    print("Caracteristicas activas del sub nivel Entretenimiento ", objetoPuntoVariacion.obtenerConfiguracionNivel("Entretenimiento"))

inicializar()
