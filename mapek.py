import random

import aprendizaje_automatico
import punto_variacion
import docker


class Mapek:
    def __init__(self):
        self._puntoVariacion = None
        self._reglaAdaptacion = None

    def monitoreo(self, mc):
        numRandom = random.randint(1, 350)
        print(numRandom)
        configuracion = aprendizaje_automatico.arbolesAleatoriosInverso("data/datos_redesneuronalesprofundas.csv", numRandom)
        print(configuracion)
        self.analizar(mc, configuracion, numRandom)

    def analizar(self, mc, configuracion, reglaAdaptacion):
        self.conocimiento(configuracion, mc, reglaAdaptacion)
        self.planificar()

    def planificar(self):
        contenedores = self._puntoVariacion.obtenerConfiguracion()
        self.ejecutar(contenedores)

    def ejecutar(self, contenedores):
        client = docker.from_env()
        for container in client.containers.list(all=True):
            if (container.name in contenedores):
                cont = client.containers.get(container.id)
                if (contenedores[container.name] == True and cont.status == "exited"):
                    cont.start()
                    print(f"contenedor {container.name} iniciado")
                elif (contenedores[container.name] == False and cont.status == "running"):
                    cont.stop()
                    print(f"contenedor {container.name} detenido")


    def conocimiento(self, configuracion, mc, reglaAdaptacion):
        self._puntoVariacion = punto_variacion.PuntoVariacion(configuracion, mc, "gestor_aire")
        self._reglaAdaptacion = reglaAdaptacion

    def getConocimiento(self):
        return self._puntoVariacion

    def getReglaAdaptacion(self):
        return self._reglaAdaptacion
