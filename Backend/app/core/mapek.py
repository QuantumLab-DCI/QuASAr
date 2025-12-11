import json
import docker
import datetime
import os
import time
import random 

# Importamos el módulo 'app' para leer la variable global de selección
import app as app_globals 

# Imports del sistema
from . import punto_variacion
from app.services import agente_llm
from app.services import hqc_module
from app import app_path 

# --- NUEVO: Importar Logger de Auditoría ---
from app.core.audit_logger import get_logger
# -------------------------------------------

class Mapek:
    def __init__(self):
        self._puntoVariacion = None
        self._reglaAdaptacion_ICA = None 
        self._reglaAdaptacion_CP = None
        self._reglaAdaptacion_SLA = None
        
        # --- Configurar Logger ---
        self.logger = get_logger()
        self._caso_actual = 0 # ID del caso de prueba actual
        
        # --- Variable para guardar la explicación del LLM ---
        self._razonamiento_actual = "Esperando análisis del agente..."
        
        # --- NUEVO: Traza de ejecución para el Frontend (Observabilidad) ---
        self._mapek_trace = [] 
        
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
    # ---------------------------------------------------------

    def _validar_configuracion(self, config_dict: dict, mc) -> bool:
        print("VALIDATE: Verificando la configuración del LLM...")
        
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
                print(f"VALIDATE_ERROR: Regla 'Requiere' violada. '{quien_requiere}' activo sin '{quien_es_requerido}'.")
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
                            print(f"VALIDATE_ERROR: Regla 'Obligatoria' violada en '{nombre_padre}'.")
                            return False
                
                if hijos_xor:
                    activos_xor = sum(1 for h in hijos_xor if config_dict.get(h) == True)
                    if activos_xor != 1:
                        print(f"VALIDATE_ERROR: Regla 'XOR' violada en '{nombre_padre}'. Activos: {activos_xor}")
                        return False
                
                if hijos_or:
                    activos_or = sum(1 for h in hijos_or if config_dict.get(h) == True)
                    if activos_or == 0:
                        print(f"VALIDATE_ERROR: Regla 'OR' violada en '{nombre_padre}'.")
                        return False
            
            elif config_dict.get(nombre_padre) == False:
                 for rel in c.getRelaciones:
                    if rel[1] != "Requiere":
                        hijo_key = rel[0].replace(" ", "_").lower()
                        if config_dict.get(hijo_key) == True:
                            print(f"VALIDATE_ERROR: Jerarquía violada. Padre '{nombre_padre}' inactivo.")
                            return False

        print("VALIDATE: Configuración del LLM es VÁLIDA.")
        return True

    # --- MÉTODO DE SIMULACIÓN ESTOCÁSTICA CON INTENCIÓN ---
    # MODIFICADO: Recibe caso_n para logging
    def ejecutar_escenario_manual(self, mc, target_id, caso_n=0):
        """ 
        Paso 1: MONITOREAR (Simulación Estocástica + Intención de Negocio)
        """
        self._caso_actual = caso_n # Guardar contexto para logs posteriores
        
        # Limpiar traza al inicio del ciclo
        self._mapek_trace = []
        self._registrar_paso("INICIO", f"Iniciando ciclo MAPE-K para Escenario ID {target_id}")

        escenario_actual = next((s for s in self.scenarios if s['id'] == target_id), None)
        nombre_escenario = escenario_actual['nombre'] if escenario_actual else "Desconocido/Base"

        if escenario_actual:
            # 1. Obtener rangos del JSON
            rango_ica = escenario_actual.get('rango_ica', [0, 50])
            rango_cp = escenario_actual.get('rango_cp', [0, 100])
            rango_cola = escenario_actual.get('rango_cola_qiskit', [0, 10])
            
            # 2. Generar valores REALES (Variables Ambientales)
            ica_real = random.randint(rango_ica[0], rango_ica[1])
            cp_real = random.randint(rango_cp[0], rango_cp[1])
            cola_real_qiskit = random.randint(rango_cola[0], rango_cola[1])
            prioridad = escenario_actual.get('sla_prioridad', 'RAPIDEZ')

            # 3. Generar Perfil de Usuario
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

        # Guardar contexto
        self._reglaAdaptacion_ICA = ica_real
        self._reglaAdaptacion_CP = cp_real
        self._reglaAdaptacion_SLA = prioridad
        
        # --- AUDITORIA: LOG DE PARÁMETROS ---
        self.logger.info(
            f"[CASO #{caso_n}] PARÁMETROS: "
            f"Escenario='{nombre_escenario}' | ICA={ica_real} | CP={cp_real} | "
            f"ColaQiskit={cola_real_qiskit}s | Usuario='{perfil_usuario}'"
        )
        # ------------------------------------

        # --- TRACE: MONITOREO ---
        self._registrar_paso("MONITOREO", "Sensores leídos y Perfil de usuario detectado.", {
            "ICA (Aire)": ica_real,
            "Complejidad (CP)": cp_real,
            "Latencia Qiskit": f"{cola_real_qiskit}s",
            "Intención Usuario": perfil_usuario
        })

        # Pasar los valores al análisis
        self.analizar(mc, ica_real, cp_real, prioridad, cola_real_qiskit, perfil_usuario)

    def analizar(self, mc, ica, complejidad_problema, prioridad, cola_forzada=None, perfil_usuario="Estándar"):
        """ Paso 2: ANALIZAR """
        
        # --- TRACE: ANÁLISIS ---
        self._registrar_paso("ANÁLISIS", "Detectada necesidad de adaptación. Consultando Agente Inteligente...", {
            "Motivo": "Cambio en contexto detectado",
            "Estrategia": "Consulta a LLM (Gemini)"
        })
        
        reglas_del_modelo = mc.exportar_reglas_texto()
        metricas_nisq = hqc_module.monitor_backends()
        
        # INYECCIÓN DE ESTADO SIMULADO
        if cola_forzada is not None:
            metricas_nisq["Qiskit Simulator"]["queue_time_sec"] = cola_forzada

        contexto_actual = f"""
        DATOS DEL ENTORNO EN TIEMPO REAL (Simulación Estocástica - Escenario {app_globals.escenario_activo_id}):
        
        1. **Perfil de Demanda (INTENCIÓN DE USUARIO):** "{perfil_usuario}"
           - Si es 'Deportivo', intenta activar 'Deportes' (si el aire lo permite).
           - Si es 'Familia/Adulto/Tercera Edad', activa la rama de 'Entretenimiento' correspondiente.
           - Si es 'Estándar', mantén el sistema mínimo (Desactiva Deportes y Entretenimiento).

        2. **Condiciones Ambientales:**
           - Calidad del Aire (ICA) = {ica}. (Regla: Si ICA > 100, priorizar 'Ambientes cerrados' y prohibir 'Deportes').
        
        3. **Requerimiento Computacional:**
           - Complejidad (CP) = {complejidad_problema}. (Regla: Si CP > 100, activar 'HQC' y 'Optimizacion de rutas'. Si CP <= 100, 'HQC' inactivo).

        4. **Infraestructura:**
           - Prioridad SLA: {prioridad}.
           - Estado Backends: {metricas_nisq}
        """
        
        config_dict_llm = agente_llm.obtener_configuracion_llm(contexto_actual, reglas_del_modelo)

        if not config_dict_llm:
            # --- AUDITORIA: ERROR LLM ---
            self.logger.error(f"[CASO #{self._caso_actual}] ❌ FALLO LLM: El agente devolvió una configuración vacía o inválida.")
            # ----------------------------
            self._registrar_paso("ERROR", "El Agente LLM no devolvió una configuración válida.")
            return 

        # Capturar razonamiento
        if "razonamiento" in config_dict_llm:
            self._razonamiento_actual = config_dict_llm["razonamiento"]
            
            # --- AUDITORIA: EXITO LLM ---
            self.logger.info(f"[CASO #{self._caso_actual}] ✅ LLM Respondió. Razonamiento: {self._razonamiento_actual}")
            # ----------------------------

            # --- TRACE: ANÁLISIS (RESULTADO) ---
            self._registrar_paso("ANÁLISIS (IA)", "El Agente ha tomado una decisión.", {
                "Razonamiento": self._razonamiento_actual
            })

        config_plana = self._find_features_in_json(config_dict_llm)
        
        # --- AUTO-REPARACIÓN ---
        if config_plana.get('hqc') == False:
            nodos_cuanticos = ['backend', 'algoritmo', 'qiskit_simulator', 'cirq_simulator', 'qaoa', 'vqe']
            se_apago_algo = False
            for nodo in nodos_cuanticos:
                if config_plana.get(nodo) == True:
                    config_plana[nodo] = False
                    se_apago_algo = True
            if se_apago_algo:
                self._registrar_paso("ANÁLISIS (SELF-HEALING)", "Mecanismo de defensa activado: Apagando hijos huérfanos de HQC.")
        
        # Validación formal
        config_plana_con_raiz = config_plana.copy()
        config_plana_con_raiz['gestor_aire'] = True 
        
        if not self._validar_configuracion(config_plana_con_raiz, mc):
            # --- AUDITORIA: ERROR VALIDACION ---
            self.logger.error(f"[CASO #{self._caso_actual}] ❌ FALLO VALIDACIÓN: Configuración LLM viola reglas del modelo.")
            # -----------------------------------
            self._registrar_paso("ERROR", "Configuración rechazada por validación estructural.")
            return

        configuracion_final = []
        for key, value in config_plana.items(): 
            nombre_formal = next(
                (c.getNombre for c in mc.caracteristicas 
                 if c.getNombre.replace(" ", "_").lower() == key.lower()), 
                key.replace("_", " ").capitalize()
            )
            estado = "activada" if value else "desactivada"
            configuracion_final.append(f"{nombre_formal} {estado}")

        self.conocimiento(configuracion_final, mc, ica, complejidad_problema)
        self.planificar()

    def planificar(self):
        """ Paso 3: PLANIFICAR """
        if self._puntoVariacion:
            config = self._puntoVariacion.obtenerConfiguracion()
            # --- TRACE: PLANIFICACIÓN ---
            activas = [k for k, v in config.items() if v is True]
            self._registrar_paso("PLANIFICACIÓN", "Plan de reconfiguración generado.", {
                "Estrategia": "Hot-Swap de contenedores y Backends",
                "Features a Activar": activas
            })
            self.ejecutar(config)

    def ejecutar(self, contenedores):
        """ Paso 4: EJECUTAR """
        if not contenedores: return

        # --- TRACE: EJECUCIÓN INICIO ---
        self._registrar_paso("EJECUCIÓN", "Aplicando cambios en infraestructura...", {
            "Mecanismo": "Docker API + HQC Factory",
            "Estado": "Redireccionando servicios"
        })

        client = docker.from_env()
        log_path = os.path.join(app_path, "data", "cambios.log")
        
        # --- AUDITORIA: INICIO RECONFIGURACION ---
        self.logger.info(f"[CASO #{self._caso_actual}] ⚙️ Iniciando reconfiguración de infraestructura...")
        
        with open(log_path, "a", encoding="utf-8") as log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"\n--- RECONFIGURACIÓN {timestamp} ---\n")
            
            # --- MODIFICACIÓN PARA AUDITAR CADA CONTENEDOR ---
            for container in client.containers.list(all=True):
                estado_deseado = contenedores.get(container.name)
                if estado_deseado is not None:
                    try:
                        cont = client.containers.get(container.id)
                        
                        if estado_deseado == True and cont.status == "exited":
                            cont.start()
                            log_file.write(f"[+] Contenedor '{container.name}' iniciado.\n")
                            # Log éxito activación
                            self.logger.info(f"[CASO #{self._caso_actual}] 🟢 ACTIVADO EXITO: Contenedor '{container.name}'")
                            
                        elif estado_deseado == False and cont.status == "running":
                            cont.stop()
                            log_file.write(f"[-] Contenedor '{container.name}' detenido.\n")
                            # Log éxito desactivación
                            self.logger.info(f"[CASO #{self._caso_actual}] 🔴 DESACTIVADO EXITO: Contenedor '{container.name}'")
                            
                    except Exception as e:
                        msg_err = f"EXECUTE_ERROR Docker en {container.name}: {e}"
                        print(msg_err)
                        # Log error individual
                        accion = "ACTIVAR" if estado_deseado else "DESACTIVAR"
                        self.logger.error(f"[CASO #{self._caso_actual}] ❌ ERROR AL {accion} nodo '{container.name}': {str(e)}")
            # ------------------------------------------------

        # --- EJECUCIÓN CUÁNTICA ADAPTATIVA ---
        if contenedores.get("hqc") == True:
            
            algoritmo_qaoa_activo = contenedores.get("qaoa") == True
            algoritmo_vqe_activo = contenedores.get("vqe") == True

            if algoritmo_qaoa_activo or algoritmo_vqe_activo:
                try:
                    backend_key = next(b for b in ["qiskit_simulator", "cirq_simulator"] if contenedores.get(b))
                    algoritmo = "QAOA" if algoritmo_qaoa_activo else "VQE"
                    backend_nombre = backend_key.replace("_", " ").title()

                    # ADAPTACIÓN DE CARGA
                    cp = self._reglaAdaptacion_CP
                    if cp < 250:
                        problem_size = 3
                    else:
                        problem_size = 4 

                    circuit_depth = 1
                    if cp >= 400:
                        circuit_depth = 2
                    
                    # --- TRACE: EJECUCIÓN HQC ---
                    self._registrar_paso("EJECUCIÓN (HQC)", f"Enviando carga de trabajo a {backend_nombre}.", {
                        "Algoritmo": algoritmo,
                        "Qubits (N)": problem_size**2 if algoritmo == "VQE" else problem_size, # Aprox
                        "Profundidad": circuit_depth
                    })

                    backend_adapter = hqc_module.get_backend_adapter(backend_nombre)

                    if backend_adapter:
                        unique_id = f"{app_globals.escenario_activo_id}_{int(time.time())}"
                        params = {
                            "problema_id": unique_id,
                            "complejidad_cp": cp,
                            "size": problem_size,    
                            "depth": circuit_depth   
                        }
                        
                        resultado = backend_adapter.execute_job(algoritmo=algoritmo, params=params)
                        
                        # --- TRACE: RESULTADO HQC ---
                        self._registrar_paso("FIN EJECUCIÓN HQC", "Trabajo cuántico finalizado.", {
                            "Costo Óptimo": f"{resultado.get('costo_optimo'):.4f}",
                            "Evidencia": "Generada en /data"
                        })
                        
                        with open(log_path, "a", encoding="utf-8") as log_file:
                             log_file.write(f"[⚛️] Job HQC: Costo={resultado.get('costo_optimo')}\n")
                        
                        # --- AUDITORIA: EXITO HQC ---
                        self.logger.info(f"[CASO #{self._caso_actual}] ⚛️ EXITO HQC: Job completado. Costo={resultado.get('costo_optimo')}")

                except Exception as e:
                    print(f"EXECUTE_ERROR HQC: {e}")
                    self._registrar_paso("ERROR", f"Fallo en ejecución cuántica: {e}")
                    # --- AUDITORIA: ERROR HQC ---
                    self.logger.error(f"[CASO #{self._caso_actual}] ❌ FALLO HQC: Error en ejecución cuántica: {str(e)}")
        
        # --- TRACE: FIN ---
        self._registrar_paso("FIN", "Ciclo MAPE-K completado exitosamente.")

    def conocimiento(self, configuracion, mc, ica, complejidad_problema):
        """ Paso 5: CONOCIMIENTO """
        print("KNOWLEDGE: Actualizando base de conocimiento y estado global.")
        self._puntoVariacion = punto_variacion.PuntoVariacion(configuracion, mc, "gestor_aire")

    def getConocimiento(self):
        return self._puntoVariacion

    def getReglaAdaptacion(self):
        return {
            "calidad_aire_ica": self._reglaAdaptacion_ICA,
            "complejidad_problema_cp": self._reglaAdaptacion_CP,
            "prioridad_sla": self._reglaAdaptacion_SLA,
            "razonamiento": self._razonamiento_actual 
        }
    
    # --- NUEVO GETTER PARA LA TRAZA ---
    def getTrace(self):
        """Devuelve el historial de ejecución del ciclo actual"""
        return self._mapek_trace