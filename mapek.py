import random
import aprendizaje_automatico
import punto_variacion
import docker
import datetime
import hqc_module  # <-- MODIFICACIÓN: Importa tu nuevo módulo cuántico

class Mapek:
    def __init__(self):
        self._puntoVariacion = None
        self._reglaAdaptacion = None # Almacenará la 'complejidad_problema'

    # --- MONITOREO MODIFICADO ---
    # Ahora monitorea el entorno clásico Y el cuántico.
    def monitoreo(self, mc):
        """
        Paso 1: MONITOREAR
        - Monitorea el entorno clásico (simula complejidad del problema).
        - Monitorea el entorno cuántico (simula métricas NISQ de los backends).
        """
        # 1. Monitor Clásico: Simula la complejidad del problema
        complejidad_problema = random.randint(1, 350)
        print(f"MONITOR: Complejidad del problema detectada: {complejidad_problema}")

        # 2. Monitor Cuántico: Llama al HQC para obtener métricas NISQ
        metricas_nisq = hqc_module.monitor_backends()
        print(f"MONITOR: Métricas NISQ recibidas: {metricas_nisq}")

        # Pasa todos los datos monitoreados al paso de Análisis
        self.analizar(mc, complejidad_problema, metricas_nisq)

    # --- ANÁLISIS MODIFICADO ---
    # Contiene la nueva lógica de decisión híbrida.
    def analizar(self, mc, complejidad, metricas_nisq):
        """
        Paso 2: ANALIZAR
        - Decide si se necesita el HQC basado en la complejidad.
        - Si es HQC, selecciona el mejor backend basado en métricas NISQ.
        - Obtiene la configuración de software final.
        """
        configuracion_final = []
        regla_adaptacion_ml = complejidad  # Usamos la complejidad para el ML de Oscar

        UMBRAL_HQC = 300  # Umbral para decidir si se usa el HQC

        if complejidad < UMBRAL_HQC:
            # --- CASO CLÁSICO ---
            print(f"ANALYZE: Problema simple (<{UMBRAL_HQC}). Forzando configuración clásica.")
            
            # 1. Obtenemos la config base del ML (que puede traer HQC por error)
            config_clasica_lista = aprendizaje_automatico.arbolesAleatoriosInverso(
                "data/datos_redesneuronalesprofundas.csv", regla_adaptacion_ml
            )
            # 2. Convertimos a dict para manipularla
            config_dict = aprendizaje_automatico.obtenerJSONPrediccion(config_clasica_lista)

            # 3. FORZAMOS el apagado de HQC y todos sus componentes
            config_dict["hqc"] = False
            config_dict["backend"] = False
            config_dict["algoritmo"] = False
            config_dict["optimizacion_de_rutas"] = False # La funcionalidad que lo requiere
            
            # Apagamos todos los backends y algoritmos
            for backend_key in ["qiskit_simulator", "spinq_simulator", "tql_simulator"]:
                 config_dict[backend_key] = False
            for algo_key in ["qaoa", "vqe"]:
                config_dict[algo_key] = False

            # 4. Convertir el dict modificado de nuevo a la lista de strings
            configuracion_final = []
            for key, value in config_dict.items():
                estado = "activada" if value else "desactivada"
                # Formato esperado por punto_variacion.py: "hqc activada"
                configuracion_final.append(f"{key} {estado}")
        
        else:
            # --- CASO HÍBRIDO (CLÁSICO + CUÁNTICO) ---
            print(f"ANALYZE: Problema complejo (>{UMBRAL_HQC}). Activando HQC.")

            # 1. Obtener la configuración base (clásica) del ML de Oscar
            config_clasica_lista = aprendizaje_automatico.arbolesAleatoriosInverso(
                "data/datos_redesneuronalesprofundas.csv", regla_adaptacion_ml
            )
            # Convertirla a un dict para poder modificarla
            config_dict = aprendizaje_automatico.obtenerJSONPrediccion(config_clasica_lista)

            # 2. Seleccionar el mejor backend cuántico (Lógica de decisión)
            # Fórmula de costo simple: tiempo de cola + (tasa de error * 100)
            mejor_backend = min(
                metricas_nisq,
                key=lambda b: metricas_nisq[b]['queue_time_sec'] + (metricas_nisq[b]['error_rate'] * 1000) # Ponderamos más el error
            )
            print(f"ANALYZE: Mejor backend seleccionado: {mejor_backend}")

            # 3. Forzar la configuración HQC en el dict
            # (Asume que las claves del dict son 'hqc', 'qaoa', 'qiskit_simulator', etc.)
            config_dict["hqc"] = True
            config_dict["backend"] = True
            config_dict["algoritmo"] = True
            config_dict["optimizacion_de_rutas"] = True # La funcionalidad que disparó la necesidad

            # Activa el backend elegido y desactiva los otros
            for backend_name in metricas_nisq.keys():
                # Normaliza el nombre del backend (ej: "Qiskit Simulator" -> "qiskit_simulator")
                backend_key = backend_name.replace(" ", "_").lower()
                config_dict[backend_key] = (backend_name == mejor_backend)

            # Elige un algoritmo por defecto (ej. QAOA)
            config_dict["qaoa"] = True
            config_dict["vqe"] = False
            
            # 4. Convertir el dict modificado de nuevo a la lista de strings
            configuracion_final = []
            for key, value in config_dict.items():
                estado = "activada" if value else "desactivada"
                # Formato esperado por punto_variacion.py: "hqc activada"
                configuracion_final.append(f"{key} {estado}")

            print(f"ANALYZE: Configuración híbrida final generada.")

        # 5. Pasa al paso de Conocimiento y Planificación
        self.conocimiento(configuracion_final, mc, complejidad)
        self.planificar()

    # --- PLANIFICAR (Sin cambios) ---
    def planificar(self):
        """
        Paso 3: PLANIFICAR
        - Obtiene la configuración de contenedores desde el conocimiento.
        """
        contenedores = self._puntoVariacion.obtenerConfiguracion()
        print(f"PLAN: Plan de reconfiguración Docker listo: {contenedores}")
        self.ejecutar(contenedores)

    # --- EJECUTAR MODIFICADO ---
    # Ahora maneja la ejecución clásica (Docker) Y la cuántica (HQC).
    def ejecutar(self, contenedores):
        """
        Paso 4: EJECUTAR
        - Ejecuta el plan para contenedores Docker (parte clásica).
        - Ejecuta el plan para el HQC (parte cuántica).
        """
        client = docker.from_env()
        
        # --- 1. Ejecución Clásica (Contenedores Docker) ---
        print("EXECUTE: Iniciando ejecución de contenedores Docker...")
        with open("cambios.log", "a", encoding="utf-8") as log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"\n--- RECONFIGURACIÓN a las {timestamp} ---\n")
            log_file.write(f"Regla de Adaptación (Complejidad): {self._reglaAdaptacion}\n")
            
            for container in client.containers.list(all=True):
                # Solo afecta a los contenedores Docker definidos en el plan
                if (container.name in contenedores):
                    cont = client.containers.get(container.id)
                    if (contenedores[container.name] == True and cont.status == "exited"):
                        cont.start()
                        mensaje = f"Contenedor '{container.name}' iniciado."
                        print(f"[+] {mensaje}")
                        log_file.write(f"[+] {mensaje}\n")
                    elif (contenedores[container.name] == False and cont.status == "running"):
                        cont.stop()
                        mensaje = f"Contenedor '{container.name}' detenido."
                        print(f"[-] {mensaje}")
                        log_file.write(f"[-] {mensaje}\n")

        # --- 2. Ejecución Cuántica (Llamada al módulo HQC) ---
        # Verificamos si la característica HQC está activa en el plan
        if contenedores.get("hqc") == True:
            print("EXECUTE: HQC está activo. Verificando trabajo cuántico...")
            
            # Si la funcionalidad que lo requiere está activa, se ejecuta
            if contenedores.get("optimizacion_de_rutas") == True:
                try:
                    # Extraemos la configuración cuántica del plan
                    backend_activo = next(
                        b for b in ["qiskit_simulator", "spinq_simulator", "tql_simulator"] if contenedores.get(b)
                    )
                    algoritmo_activo = next(
                        a.upper() for a in ["qaoa", "vqe"] if contenedores.get(a)
                    )

                    # Normaliza los nombres para la función
                    backend_nombre_formal = backend_activo.replace("_", " ").title() # ej: "Qiskit Simulator"
                    
                    print(f"EXECUTE: Delegando trabajo cuántico -> Algoritmo: {algoritmo_activo}, Backend: {backend_nombre_formal}")

                    # (Opcional) Pasa parámetros del problema
                    params = {"problema_id": "ruta_123", "complejidad": self._reglaAdaptacion}
                    
                    # Delegamos la ejecución al módulo cuántico
                    resultado_cuantico = hqc_module.ejecutar_quantum_job(
                        algoritmo=algoritmo_activo,
                        backend=backend_nombre_formal,
                        params=params
                    )
                    print(f"EXECUTE: Resultado cuántico recibido: {resultado_cuantico}")
                    with open("cambios.log", "a", encoding="utf-8") as log_file:
                         log_file.write(f"[⚛️] Trabajo cuántico ({algoritmo_activo} en {backend_nombre_formal}) ejecutado.\n")

                except StopIteration:
                    print("EXECUTE_ERROR: HQC activo, pero no se encontró backend o algoritmo válido en el plan.")
            else:
                print("EXECUTE: HQC activo, pero 'optimizcacion_de_rutas' no. En espera.")
        else:
            print("EXECUTE: HQC está inactivo. Omitiendo ejecución cuántica.")

    # --- CONOCIMIENTO (Sin cambios) ---
    def conocimiento(self, configuracion, mc, reglaAdaptacion):
        """
        Paso 5: CONOCIMIENTO
        - Almacena el estado actual del sistema (el punto de variación).
        """
        self._puntoVariacion = punto_variacion.PuntoVariacion(configuracion, mc, "gestor_aire")
        self._reglaAdaptacion = reglaAdaptacion # Guardamos la regla de adaptación (complejidad)

    def getConocimiento(self):
        return self._puntoVariacion

    def getReglaAdaptacion(self):
        return self._reglaAdaptacion
