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


#funcion que retorna el arbol completo de caracteristicas
@app.get("/obtenerArbol")
async def obtenerCaracteristicas():
    return mc.obtenerArbol()

#función que retorna las relaciones de una caracteristica
@app.get("/obtenerRelacionesCaracteristica")
async def obtenerRelacionesCaracteristica(caracteristica : str):
    return mc.obtenerRelacionesCaracteristica(caracteristica)

#función que retorna todas las relaciones del mc
@app.get("/obtenerRelacionesMC")
async def obtenerRelacionesMC():
    return mc.obtenerRelacionesMC()

def inicializar():
    #Generar el grafo para permutar todos los posibles estados del modelo
    mc = grafo_mc.generarPosiblesEstados()
    #Asociar una regla de adaptación para cada punto de variación creado en la permutación
    aprendizaje_automatico.guardarPredicciones(
        aprendizaje_automatico.redesNeuronales("data/dataset.csv", "data/datos.csv"),
        "data/datos_redesneuronales.csv")

    #Crear una regla adaptación, idealmente debe ser un numero random
    reglaAdaptacion1 = 250.2
    #Entrego un numero aleatorio random, que asimila ser una regla de adaptación, el cual a partir de lo anterior clasifica un punto de variación
    #Esta clasificación se realiza por medio del algoritmo de clasificación de arboles aleatorios
    puntoVariacion1 = aprendizaje_automatico.arbolesAleatoriosInverso("data/datos_redesneuronales.csv", reglaAdaptacion1)
    #presento el punto de variación 1
    print("Punto de variación 1, ", puntoVariacion1)

    objetoPuntoVariacion = punto_variacion.PuntoVariacion(puntoVariacion1,mc)
    print("JSON con configuracion ", objetoPuntoVariacion.obtenerConfiguracion())
    print("Caracteristicas activas del sub nivel Turismo ",objetoPuntoVariacion.obtenerConfiguracionNivel("Turismo"))
    print("Caracteristicas activas del sub nivel Entretenimiento ", objetoPuntoVariacion.obtenerConfiguracionNivel("Entretenimiento"))

inicializar()

