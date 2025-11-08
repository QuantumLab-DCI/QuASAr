import random
import aprendizaje_automatico
import punto_variacion
import docker
import datetime
import hqc_module

class Mapek:
    def __init__(self):
        self._puntoVariacion = None
        # Almacenamos ambas reglas por separado
        self._reglaAdaptacion_ICA = None 
        self._reglaAdaptacion_CP = None

    def monitoreo(self, mc):
        """
        Paso 1: MONITOREAR (Lógica de Tesis Combinada)
        - Simula los DOS contextos de adaptación.
        """
        
        # --- 1. Simulación del Contexto Clásico (Tesis de Oscar) ---
        # El ICA (Índice de Calidad del Aire)
        # Valores de ejemplo: 50 (Bueno), 150 (Regular), 250 (Malo)
        ica_simulado = random.choice([50, 150, 250])
        print(f"MONITOR (Clásico): Calidad del Aire (ICA) detectada: {ica_simulado}")
        
        # --- 2. Simulación del Contexto Cuántico (Tu Tesis) ---
        # La Complejidad del Problema (CP) de optimización
        # Valores de ejemplo: 10 (Simple), 350 (Complejo)
        cp_simulado = random.choice([10, 350])
        print(f"MONITOR (Cuántico): Complejidad de Problema (CP) detectada: {cp_simulado}")

        # 3. Pasa ambos contextos al paso de Análisis
        self.analizar(mc, ica_simulado, cp_simulado)

    def analizar(self, mc, ica, complejidad_problema):
        """
        Paso 2: ANALIZAR
        - Aplica reglas de adaptación para AMBOS contextos.
        """
        print(f"ANALYZE: Iniciando análisis con ICA={ica} y CP={complejidad_problema}")
        
        # Obtenemos la config base del ML (para Turismo, Entretenimiento, etc.)
        # Usamos el ICA como la regla para el ML clásico
        config_clasica_lista = aprendizaje_automatico.arbolesAleatoriosInverso(
            "data/datos_redesneuronalesprofundas.csv", ica
        )
        config_dict = aprendizaje_automatico.obtenerJSONPrediccion(config_clasica_lista)
        
        # --- INICIO LÓGICA DE ADAPTACIÓN (TESIS DE OSCAR) ---
        UMBRAL_ICA_PELIGROSO = 100 # ej: Si ICA > 100, no hacer deporte

        if ica > UMBRAL_ICA_PELIGROSO:
            print(f"ANALYZE (Clásico): ICA={ica} es peligroso. Desactivando features de exterior.")
            # Forzamos apagado de features de exterior por salud
            config_dict["deportes"] = False
            config_dict["ambientes_abiertos"] = False
            # Forzamos encendido de features de interior
            config_dict["ambientes_cerrados"] = True
        else:
            print(f"ANALYZE (Clásico): ICA={ica} es seguro. Features de exterior permitidas.")
            # La configuración del ML (que ya tiene 'deportes' y 'ambientes_abiertos')
            # se mantiene como está.
        
        # --- FIN LÓGICA CLÁSICA ---


        # --- INICIO LÓGICA DE ADAPTACIÓN (TU TESIS) ---
        UMBRAL_HQC = 300 # Regla de tu tesis

        if complejidad_problema < UMBRAL_HQC:
            # --- CASO CLÁSICO (Lógica Explícita) ---
            print(f"ANALYZE (Cuántico): CP={complejidad_problema} es simple. Forzando APAGADO de HQC.")

            config_dict["hqc"] = False
            config_dict["backend"] = False
            config_dict["algoritmo"] = False
            config_dict["optimizacion_de_rutas"] = False
            
            for backend_key in ["qiskit_simulator", "spinq_simulator", "tql_simulator"]:
                 if backend_key in config_dict: config_dict[backend_key] = False
            for algo_key in ["qaoa", "vqe"]:
                if algo_key in config_dict: config_dict[algo_key] = False

        else:
            # --- CASO HÍBRIDO (Lógica Explícita) ---
            print(f"ANALYZE (Cuántico): CP={complejidad_problema} es complejo. Activando HQC.")

            metricas_nisq = hqc_module.monitor_backends()
            print(f"ANALYZE: Métricas NISQ recibidas: {metricas_nisq}")
            
            mejor_backend = min(
                metricas_nisq,
                key=lambda b: metricas_nisq[b]['queue_time_sec'] + (metricas_nisq[b]['error_rate'] * 1000)
            )
            print(f"ANALYZE: Mejor backend HQC seleccionado: {mejor_backend}")

            config_dict["hqc"] = True
            config_dict["backend"] = True
            config_dict["algoritmo"] = True
            config_dict["optimizacion_de_rutas"] = True 

            for backend_name in metricas_nisq.keys():
                backend_key = backend_name.replace(" ", "_").lower()
                if backend_key in config_dict:
                    config_dict[backend_key] = (backend_name == mejor_backend)

            config_dict["qaoa"] = True
            config_dict["vqe"] = False
        
        # --- FIN LÓGICA CUÁNTICA ---

        
        # 4. Convertir a lista de strings
        configuracion_final = []
        for key, value in config_dict.items():
            estado = "activada" if value else "desactivada"
            configuracion_final.append(f"{key} {estado}")

        # 5. Pasa al paso de Conocimiento y Planificación
        self.conocimiento(configuracion_final, mc, ica, complejidad_problema)
        self.planificar() 

    # ... (planificar() y ejecutar() no necesitan cambios) ...

    def planificar(self):
        """ Paso 3: PLANIFICAR """
        contenedores = self._puntoVariacion.obtenerConfiguracion()
        print(f"PLAN: Plan de reconfiguración Docker listo: {contenedores}")
        self.ejecutar(contenedores)

    def ejecutar(self, contenedores):
        """ Paso 4: EJECUTAR """
        client = docker.from_env()
        
        print("EXECUTE: Iniciando ejecución de contenedores Docker...")
        with open("cambios.log", "a", encoding="utf-8") as log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"\n--- RECONFIGURACIÓN a las {timestamp} ---\n")
            log_file.write(f"Regla de Adaptación (ICA): {self._reglaAdaptacion_ICA}\n")
            log_file.write(f"Regla de Adaptación (CP): {self._reglaAdaptacion_CP}\n")
            
            for container in client.containers.list(all=True):
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

        # --- Ejecución Cuántica ---
        if contenedores.get("hqc") == True:
            print("EXECUTE: HQC está activo. Verificando trabajo cuántico...")
            
            if contenedores.get("optimizacion_de_rutas") == True:
                try:
                    backend_activo = next(
                        b for b in ["qiskit_simulator", "spinq_simulator", "tql_simulator"] if contenedores.get(b)
                    )
                    algoritmo_activo = next(
                        a.upper() for a in ["qaoa", "vqe"] if contenedores.get(a)
                    )
                    backend_nombre_formal = backend_activo.replace("_", " ").title()
                    
                    print(f"EXECUTE: Delegando trabajo cuántico -> Algoritmo: {algoritmo_activo}, Backend: {backend_nombre_formal}")
                    # Pasamos la complejidad del problema al job cuántico
                    params = {"problema_id": "ruta_123", "complejidad": self._reglaAdaptacion_CP} 
                    
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

    def conocimiento(self, configuracion, mc, ica, complejidad_problema):
        """ Paso 5: CONOCIMIENTO """
        self._puntoVariacion = punto_variacion.PuntoVariacion(configuracion, mc, "gestor_aire")
        # Guardamos ambas reglas
        self._reglaAdaptacion_ICA = ica
        self._reglaAdaptacion_CP = complejidad_problema

    def getConocimiento(self):
        return self._puntoVariacion

    def getReglaAdaptacion(self):
        # Devolvemos un dict con ambas reglas
        return {
            "calidad_aire_ica": self._reglaAdaptacion_ICA,
            "complejidad_problema_cp": self._reglaAdaptacion_CP
        }