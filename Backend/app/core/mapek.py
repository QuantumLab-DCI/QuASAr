import json
import docker
import datetime
import os
import time
import random 
import app as app_globals 

# Imports del sistema
from . import punto_variacion
from app.services import agente_llm
from app.services import hqc_module
from app import app_path 

class Mapek:
    def __init__(self):
        self._puntoVariacion = None
        self._reglaAdaptacion_ICA = None 
        self._reglaAdaptacion_CP = None
        self._reglaAdaptacion_SLA = None
        
        # --- Variable para guardar la explicación del LLM ---
        self._razonamiento_actual = "Esperando análisis del agente..."
        
        # --- Traza de ejecución para el Frontend (Observabilidad) ---
        self._mapek_trace = [] 
        
        # --- NUEVAS VARIABLES DE ESTADO PARA LOGGING ---
        self.current_case_id = 0
        self.current_scenario_id = 0
        self.context_str = "" # Guardará los parámetros para el log
        # -----------------------------------------------

        # Cargar escenarios en memoria al iniciar
        self.scenarios = []
        try:
            json_path = os.path.join(app_path, 'data', 'scenarios.json')
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.scenarios = json.load(f)
                print(f"✅ MAPE-K: Cargados {len(self.scenarios)} escenarios para modo interactivo.")
        except Exception as e:
            print(f"⚠️ MAPE-K: Error cargando scenarios.json: {e}")

    # --- NUEVO: SISTEMA DE LOGGING A ARCHIVO (AUDITORÍA) ---
    def registrar_log_archivo(self, nivel, mensaje):
        """
        Escribe en data/historial_ejecucion.log con formato estructurado.
        Persiste los datos aunque se reinicie el servidor.
        """
        try:
            log_dir = os.path.join(app_path, "data")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            log_path = os.path.join(log_dir, "historial_ejecucion.log")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Formato: [CASO #X] [FECHA] [ESCENARIO Y] [NIVEL] MENSAJE
            linea = f"[CASO #{self.current_case_id}] [{timestamp}] [ESCENARIO {self.current_scenario_id}] [{nivel}] {mensaje}"
            
            # Si es un error crítico o el inicio, agregamos el contexto de parámetros
            if nivel in ["START", "LLM_ERROR", "CRITICAL_FAILURE"] and self.context_str:
                linea += f" || PARAMS: {self.context_str}"
                
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(linea + "\n")
        except Exception as e:
            print(f"⚠️ Error escribiendo log de archivo: {e}")
    # -------------------------------------------------------

    def _find_features_in_json(self, data: dict) -> dict:
        features = {}
        if isinstance(data, dict):
            for k, v in data.items():
                key_normalizada = k.replace(" ", "_").lower()
                if isinstance(v, bool):
                    features[key_normalizada] = v
                elif isinstance(v, dict):
                    features.update(self._find_features_in_json(v))
        return features

    # --- Helper para registrar pasos en el timeline (Frontend) ---
    def _registrar_paso(self, fase, mensaje, detalles=None):
        """Guarda un evento en la traza de ejecución para el frontend"""
        paso = {
            "fase": fase,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "mensaje": mensaje,
            "detalles": detalles
        }
        self._mapek_trace.append(paso)
        print(f"[{fase}] {mensaje}")

    def _validar_configuracion(self, config_dict: dict, mc) -> bool:
        print("VALIDATE: Verificando la configuración del LLM...")
        
        # (Lógica de validación original resumida para brevedad, no cambia la lógica)
        # ... [Mantenemos tu lógica de validación original aquí] ...
        
        # Validar 'Requiere'
        reglas_requiere = []
        for c in mc.caracteristicas:
            for rel in c.getRelaciones:
                if rel[1] == "Requiere":
                    req_key = c.getNombre.replace(" ", "_").lower()
                    req_val = rel[0].replace(" ", "_").lower()
                    reglas_requiere.append((req_key, req_val))

        for (quien_requiere, quien_es_requerido) in reglas_requiere:
            if config_dict.get(quien_requiere) and not config_dict.get(quien_es_requerido):
                msg = f"Regla 'Requiere' violada. '{quien_requiere}' activo sin '{quien_es_requerido}'."
                print(f"VALIDATE_ERROR: {msg}")
                self.registrar_log_archivo("VALIDATION_FAIL", msg) # <--- LOG
                return False

        # Validar Jerarquía
        for c in mc.caracteristicas:
            nombre_padre = c.getNombre.replace(" ", "_").lower()
            if config_dict.get(nombre_padre) == True:
                hijos_xor = [r[0].replace(" ", "_").lower() for r in c.getRelaciones if r[1] == "XOR"]
                hijos_or = [r[0].replace(" ", "_").lower() for r in c.getRelaciones if r[1] == "OR"]
                for rel in c.getRelaciones:
                    if rel[1] == "Obligatoria":
                        hijo_key = rel[0].replace(" ", "_").lower()
                        if not config_dict.get(hijo_key):
                            self.registrar_log_archivo("VALIDATION_FAIL", f"Obligatoria violada en {nombre_padre}")
                            return False
                if hijos_xor:
                    activos_xor = sum(1 for h in hijos_xor if config_dict.get(h) == True)
                    if activos_xor != 1:
                        self.registrar_log_archivo("VALIDATION_FAIL", f"XOR violada en {nombre_padre}")
                        return False
                if hijos_or:
                    activos_or = sum(1 for h in hijos_or if config_dict.get(h) == True)
                    if activos_or == 0:
                        self.registrar_log_archivo("VALIDATION_FAIL", f"OR violada en {nombre_padre}")
                        return False
            elif config_dict.get(nombre_padre) == False:
                 for rel in c.getRelaciones:
                    if rel[1] != "Requiere":
                        hijo_key = rel[0].replace(" ", "_").lower()
                        if config_dict.get(hijo_key) == True:
                            self.registrar_log_archivo("VALIDATION_FAIL", f"Jerarquía violada (Hijo activo sin Padre {nombre_padre})")
                            return False

        print("VALIDATE: Configuración del LLM es VÁLIDA.")
        return True

    # --- MÉTODO MODIFICADO: AHORA RECIBE 'case_number' ---
    def ejecutar_escenario_manual(self, mc, target_id, case_number):
        """ 
        Paso 1: MONITOREAR (Simulación Estocástica + Intención de Negocio)
        """
        # Inicializamos variables de log
        self.current_case_id = case_number
        self.current_scenario_id = target_id
        self._mapek_trace = []

        escenario_actual = next((s for s in self.scenarios if s['id'] == target_id), None)

        if escenario_actual:
            rango_ica = escenario_actual.get('rango_ica', [0, 50])
            rango_cp = escenario_actual.get('rango_cp', [0, 100])
            rango_cola = escenario_actual.get('rango_cola_qiskit', [0, 10])
            
            ica_real = random.randint(rango_ica[0], rango_ica[1])
            cp_real = random.randint(rango_cp[0], rango_cp[1])
            cola_real_qiskit = random.randint(rango_cola[0], rango_cola[1])
            prioridad = escenario_actual.get('sla_prioridad', 'RAPIDEZ')

            perfiles = [
                "Turista Estándar (Solo Rutas)",
                "Grupo Deportivo (Requiere Deportes)",
                "Adulto Mayor (Requiere Entr. Tercera Edad)",
                "Familia con Niños (Requiere Entr. Familiar)",
                "Evento Nocturno (Requiere Entr. Adulto)"
            ]
            perfil_usuario = random.choice(perfiles)
            
        else:
            print(f"⚠️ Escenario ID {target_id} no encontrado. Usando valores base.")
            ica_real = 50; cp_real = 10; prioridad = "RAPIDEZ"; cola_real_qiskit = 5; perfil_usuario = "Estándar"

        # --- PREPARAR CONTEXTO PARA LOGGING ---
        self.context_str = f"ICA={ica_real}, CP={cp_real}, SLA='{prioridad}', ColaQiskit={cola_real_qiskit}s, Perfil='{perfil_usuario}'"
        
        # 1. LOG DE INICIO (HEADER DEL CASO)
        self.registrar_log_archivo("START", "--- INICIO DE CICLO DE ADAPTACIÓN ---")
        
        # Guardar contexto global
        self._reglaAdaptacion_ICA = ica_real
        self._reglaAdaptacion_CP = cp_real
        self._reglaAdaptacion_SLA = prioridad
        
        self._registrar_paso("MONITOREO", "Sensores leídos y Perfil detectado.", {
            "ICA": ica_real, "CP": cp_real, "SLA": prioridad, "Perfil": perfil_usuario
        })

        self.analizar(mc, ica_real, cp_real, prioridad, cola_real_qiskit, perfil_usuario)

    def analizar(self, mc, ica, complejidad_problema, prioridad, cola_forzada=None, perfil_usuario="Estándar"):
        """ Paso 2: ANALIZAR """
        
        self._registrar_paso("ANÁLISIS", "Detectada necesidad de adaptación. Consultando Agente...", {
            "Estrategia": "LLM Generativo (Gemini)"
        })
        
        reglas_del_modelo = mc.exportar_reglas_texto()
        metricas_nisq = hqc_module.monitor_backends()
        if cola_forzada is not None:
            metricas_nisq["Qiskit Simulator"]["queue_time_sec"] = cola_forzada

        contexto_actual = f"""
        DATOS DEL ENTORNO EN TIEMPO REAL (Simulación Estocástica - Escenario {app_globals.escenario_activo_id}):
        1. **Perfil de Demanda:** "{perfil_usuario}"
        2. **Condiciones Ambientales:** ICA = {ica}.
        3. **Requerimiento Computacional:** CP = {complejidad_problema}.
        4. **Infraestructura:** SLA: {prioridad}, Estado Backends: {metricas_nisq}
        """
        
        config_dict_llm = agente_llm.obtener_configuracion_llm(contexto_actual, reglas_del_modelo)

        if not config_dict_llm:
            msg = "El Agente LLM devolvió una configuración vacía o hubo error de red."
            self._registrar_paso("ERROR", msg)
            self.registrar_log_archivo("LLM_ERROR", msg) # <--- LOG ERROR
            return 

        if "razonamiento" in config_dict_llm:
            self._razonamiento_actual = config_dict_llm["razonamiento"]
            self._registrar_paso("ANÁLISIS (IA)", "Decisión tomada.", {"Razonamiento": self._razonamiento_actual})
            # <--- LOG RAZONAMIENTO
            self.registrar_log_archivo("LLM_DECISION", f"Razonamiento: {self._razonamiento_actual}")

        config_plana = self._find_features_in_json(config_dict_llm)
        
        # Auto-reparación simple
        if config_plana.get('hqc') == False:
            nodos_cuanticos = ['backend', 'algoritmo', 'qiskit_simulator', 'cirq_simulator', 'qaoa', 'vqe']
            for nodo in nodos_cuanticos:
                if config_plana.get(nodo) == True:
                    config_plana[nodo] = False

        config_plana_con_raiz = config_plana.copy()
        config_plana_con_raiz['gestor_aire'] = True 
        
        if not self._validar_configuracion(config_plana_con_raiz, mc):
            self._registrar_paso("ERROR", "Configuración rechazada por validación estructural.")
            return

        configuracion_final = []
        features_activas_log = [] # Para el log
        for key, value in config_plana.items(): 
            nombre_formal = next(
                (c.getNombre for c in mc.caracteristicas 
                 if c.getNombre.replace(" ", "_").lower() == key.lower()), 
                key.replace("_", " ").capitalize()
            )
            estado = "activada" if value else "desactivada"
            configuracion_final.append(f"{nombre_formal} {estado}")
            if value: features_activas_log.append(nombre_formal)

        # <--- LOG PLAN
        self.registrar_log_archivo("PLAN", f"Features activas: {features_activas_log}")

        self.conocimiento(configuracion_final, mc, ica, complejidad_problema)
        self.planificar()

    def planificar(self):
        """ Paso 3: PLANIFICAR """
        if self._puntoVariacion:
            config = self._puntoVariacion.obtenerConfiguracion()
            activas = [k for k, v in config.items() if v is True]
            self._registrar_paso("PLANIFICACIÓN", "Plan generado.", {"Features a Activar": activas})
            self.ejecutar(config)

    def ejecutar(self, contenedores):
        """ Paso 4: EJECUTAR (CON LOGS DETALLADOS DE DOCKER) """
        if not contenedores: return

        self._registrar_paso("EJECUCIÓN", "Aplicando cambios en infraestructura...")
        self.registrar_log_archivo("EXECUTION_START", "Iniciando reconfiguración de contenedores...")

        client = docker.from_env()
        # Log técnico local (legacy)
        log_path_legacy = os.path.join(app_path, "data", "cambios.log")
        
        try:
            # Obtenemos lista de contenedores reales para verificar existencia
            all_containers = {c.name: c for c in client.containers.list(all=True)}
            
            with open(log_path_legacy, "a", encoding="utf-8") as log_file:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_file.write(f"\n--- RECONFIGURACIÓN {timestamp} ---\n")
                
                for nombre_cont, debe_estar_activo in contenedores.items():
                    # Verificamos si el contenedor existe en Docker
                    if nombre_cont in all_containers:
                        container = all_containers[nombre_cont]
                        try:
                            if debe_estar_activo and container.status == "exited":
                                container.start()
                                msg = f"Contenedor '{nombre_cont}' INICIADO correctamente."
                                log_file.write(f"[+] {msg}\n")
                                self.registrar_log_archivo("NODE_SUCCESS", f"Activado: {nombre_cont}") # <--- LOG
                                self._registrar_paso("EJECUCIÓN", msg)
                            
                            elif not debe_estar_activo and container.status == "running":
                                container.stop()
                                msg = f"Contenedor '{nombre_cont}' DETENIDO correctamente."
                                log_file.write(f"[-] {msg}\n")
                                self.registrar_log_archivo("NODE_SUCCESS", f"Desactivado: {nombre_cont}") # <--- LOG
                                self._registrar_paso("EJECUCIÓN", msg)
                            
                            # Si ya estaba en el estado deseado, no logueamos nada en auditoría para no saturar
                        except Exception as e_cont:
                            err_msg = f"Error cambiando estado de {nombre_cont}: {str(e_cont)}"
                            self.registrar_log_archivo("NODE_FAILURE", err_msg) # <--- LOG FAILURE
                            self._registrar_paso("ERROR", err_msg)
                    else:
                        # El feature está en el modelo, pero no hay contenedor Docker con ese nombre exacto
                        if debe_estar_activo: # Solo reportamos si intentamos prenderlo
                            warn_msg = f"No se encontró contenedor Docker: {nombre_cont}"
                            self.registrar_log_archivo("NODE_WARNING", warn_msg) # <--- LOG WARNING

        except Exception as e:
            print(f"EXECUTE_ERROR Docker: {e}")
            self.registrar_log_archivo("DOCKER_CRASH", f"Error general de Docker: {e}")

        # --- EJECUCIÓN CUÁNTICA ---
        if contenedores.get("hqc") == True:
            # (Lógica HQC idéntica a la original, omito detalles por brevedad pero mantengo la estructura)
            algoritmo_qaoa_activo = contenedores.get("qaoa") == True
            algoritmo_vqe_activo = contenedores.get("vqe") == True

            if algoritmo_qaoa_activo or algoritmo_vqe_activo:
                try:
                    backend_key = next(b for b in ["qiskit_simulator", "cirq_simulator"] if contenedores.get(b))
                    algoritmo = "QAOA" if algoritmo_qaoa_activo else "VQE"
                    backend_nombre = backend_key.replace("_", " ").title()
                    
                    cp = self._reglaAdaptacion_CP
                    problem_size = 3 if cp < 250 else 4 
                    circuit_depth = 1 if cp < 400 else 2
                    
                    self._registrar_paso("EJECUCIÓN (HQC)", f"Enviando carga a {backend_nombre}...", {"Algoritmo": algoritmo})
                    self.registrar_log_archivo("HQC_INFO", f"Iniciando Job {algoritmo} en {backend_nombre} (CP={cp})")

                    backend_adapter = hqc_module.get_backend_adapter(backend_nombre)
                    if backend_adapter:
                        unique_id = f"{app_globals.escenario_activo_id}_{int(time.time())}"
                        params = {"problema_id": unique_id, "complejidad_cp": cp, "size": problem_size, "depth": circuit_depth}
                        
                        resultado = backend_adapter.execute_job(algoritmo=algoritmo, params=params)
                        
                        self._registrar_paso("FIN EJECUCIÓN HQC", "Finalizado.", {"Costo": f"{resultado.get('costo_optimo'):.4f}"})
                        # Log resultado
                        self.registrar_log_archivo("HQC_SUCCESS", f"Job finalizado. Costo: {resultado.get('costo_optimo')}")

                except Exception as e:
                    print(f"EXECUTE_ERROR HQC: {e}")
                    self._registrar_paso("ERROR", f"Fallo en ejecución cuántica: {e}")
                    self.registrar_log_archivo("HQC_FAILURE", f"Error: {e}")
        
        self.registrar_log_archivo("SUCCESS", "Ciclo completado.")
        self._registrar_paso("FIN", "Ciclo MAPE-K completado exitosamente.")

    def conocimiento(self, configuracion, mc, ica, complejidad_problema):
        print("KNOWLEDGE: Actualizando base de conocimiento y estado global.")
        self._puntoVariacion = punto_variacion.PuntoVariacion(configuracion, mc, "gestor_aire")

    def getConocimiento(self): return self._puntoVariacion
    def getReglaAdaptacion(self):
        return {
            "calidad_aire_ica": self._reglaAdaptacion_ICA,
            "complejidad_problema_cp": self._reglaAdaptacion_CP,
            "prioridad_sla": self._reglaAdaptacion_SLA,
            "razonamiento": self._razonamiento_actual 
        }
    def getTrace(self): return self._mapek_trace