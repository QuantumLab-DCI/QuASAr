import random

import aprendizaje_automatico
import punto_variacion
import docker
import datetime # <-- AÑADIR ESTE IMPORT


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
        # Abrir el archivo de log en modo 'append' (añadir al final)
        with open("cambios.log", "a", encoding="utf-8") as log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"\n--- RECONFIGURACIÓN a las {timestamp} ---\n")
            
            for container in client.containers.list(all=True):
                if (container.name in contenedores):
                    cont = client.containers.get(container.id)
                    if (contenedores[container.name] == True and cont.status == "exited"):
                        cont.start()
                        mensaje = f"Contenedor '{container.name}' iniciado."
                        print(mensaje)
                        log_file.write(f"[+] {mensaje}\n") # <-- AÑADIR
                    elif (contenedores[container.name] == False and cont.status == "running"):
                        cont.stop()
                        mensaje = f"Contenedor '{container.name}' detenido."
                        print(mensaje)
                        log_file.write(f"[-] {mensaje}\n") # <-- AÑADIR


    def conocimiento(self, configuracion, mc, reglaAdaptacion):
        self._puntoVariacion = punto_variacion.PuntoVariacion(configuracion, mc, "gestor_aire")
        self._reglaAdaptacion = reglaAdaptacion

    def getConocimiento(self):
        return self._puntoVariacion

    def getReglaAdaptacion(self):
        return self._reglaAdaptacion
