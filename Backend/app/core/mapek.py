import json
import docker
import datetime
import os
import time
import random # <--- IMPORTANTE: Para simulación estocástica

# Importamos el módulo 'app' para leer la variable global de selección
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
        
        # --- NUEVO: Variable para guardar la explicación del LLM ---
        self._razonamiento_actual = "Esperando análisis del agente..."
        
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
    def ejecutar_escenario_manual(self, mc, target_id):
        """ 
        Paso 1: MONITOREAR (Simulación Estocástica + Intención de Negocio)
        Genera valores aleatorios DENTRO de los rangos y un Perfil de Usuario.
        """
        escenario_actual = next((s for s in self.scenarios if s['id'] == target_id), None)

        if escenario_actual:
            print(f"\n🕹️ [MONITOR] Activando Escenario ID {target_id}: {escenario_actual['nombre']}")
            print(f"   🎲 Generando condiciones estocásticas y perfil de usuario...")
            
            # 1. Obtener rangos del JSON (o usar defaults si no existen)
            rango_ica = escenario_actual.get('rango_ica', [0, 50])
            rango_cp = escenario_actual.get('rango_cp', [0, 100])
            rango_cola = escenario_actual.get('rango_cola_qiskit', [0, 10])
            
            # 2. Generar valores REALES para esta ejecución (Variables Ambientales)
            ica_real = random.randint(rango_ica[0], rango_ica[1])
            cp_real = random.randint(rango_cp[0], rango_cp[1])
            cola_real_qiskit = random.randint(rango_cola[0], rango_cola[1])
            prioridad = escenario_actual.get('sla_prioridad', 'RAPIDEZ')

            # 3. Generar Perfil de Usuario (Variable de Negocio para cambiar el diagrama)
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

        print(f"🔎 SENSADO REAL: Perfil='{perfil_usuario}' | ICA={ica_real} | CP={cp_real} | Cola={cola_real_qiskit}s")
        
        # Guardar contexto para API
        self._reglaAdaptacion_ICA = ica_real
        self._reglaAdaptacion_CP = cp_real
        self._reglaAdaptacion_SLA = prioridad
        
        # Pasar los valores aleatorios y el perfil al análisis
        self.analizar(mc, ica_real, cp_real, prioridad, cola_real_qiskit, perfil_usuario)

    def analizar(self, mc, ica, complejidad_problema, prioridad, cola_forzada=None, perfil_usuario="Estándar"):
        """ Paso 2: ANALIZAR (Con Agente LLM y Contexto Completo) """
        print(f"🧠 ANALYZE: Consultando al LLM...")
        
        reglas_del_modelo = mc.exportar_reglas_texto()
        metricas_nisq = hqc_module.monitor_backends()
        
        # INYECCIÓN DE ESTADO SIMULADO (Desde la generación estocástica)
        if cola_forzada is not None:
            metricas_nisq["Qiskit Simulator"]["queue_time_sec"] = cola_forzada
            if cola_forzada > 60:
                 print(f"   ⚠️ [DEMO] Infraestructura reporta congestión en Qiskit: {cola_forzada}s")

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
            print("ANALYZE_ERROR: Configuración vacía del LLM.")
            return 

        # --- NUEVO: Capturar y guardar el razonamiento del LLM ---
        if "razonamiento" in config_dict_llm:
            self._razonamiento_actual = config_dict_llm["razonamiento"]
            print(f"🤖 RAZONAMIENTO LLM: {self._razonamiento_actual}")
        # -----------------------------------------------------------

        config_plana = self._find_features_in_json(config_dict_llm)
        
        # --- AUTO-REPARACIÓN (SELF-HEALING) ---
        if config_plana.get('hqc') == False:
            nodos_cuanticos = ['backend', 'algoritmo', 'qiskit_simulator', 'cirq_simulator', 'qaoa', 'vqe']
            for nodo in nodos_cuanticos:
                if config_plana.get(nodo) == True:
                    print(f"   🔧 SELF-HEALING: Forzando apagado de '{nodo}' porque HQC está inactivo.")
                    config_plana[nodo] = False
        
        # Validación formal
        config_plana_con_raiz = config_plana.copy()
        config_plana_con_raiz['gestor_aire'] = True 
        
        if not self._validar_configuracion(config_plana_con_raiz, mc):
            print("ANALYZE_ERROR: Configuración INVÁLIDA rechazada por el sistema.")
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

        print(f"ANALYZE: Configuración decidida: {config_plana}")
        
        self.conocimiento(configuracion_final, mc, ica, complejidad_problema)
        self.planificar()

    def planificar(self):
        """ Paso 3: PLANIFICAR """
        if self._puntoVariacion:
            print(f"PLAN: Plan de despliegue generado.")
            self.ejecutar(self._puntoVariacion.obtenerConfiguracion())

    def ejecutar(self, contenedores):
        """ Paso 4: EJECUTAR (Con Adaptación de Carga y Protección) """
        
        if not contenedores: return

        client = docker.from_env()
        print("EXECUTE: Aplicando cambios en infraestructura...")
        
        log_path = os.path.join(app_path, "data", "cambios.log")
        with open(log_path, "a", encoding="utf-8") as log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"\n--- RECONFIGURACIÓN {timestamp} ---\n")
            
            escenario_actual = next((s for s in self.scenarios if s['id'] == app_globals.escenario_activo_id), None)
            nombre_escenario = escenario_actual['nombre'] if escenario_actual else f"ID {app_globals.escenario_activo_id}"
            
            log_file.write(f"Escenario Activo: {nombre_escenario}\n")
            log_file.write(f"Contexto: ICA={self._reglaAdaptacion_ICA}, CP={self._reglaAdaptacion_CP}, SLA={self._reglaAdaptacion_SLA}\n")
            
            try:
                for container in client.containers.list(all=True):
                    estado_deseado = contenedores.get(container.name)
                    if estado_deseado is not None:
                        cont = client.containers.get(container.id)
                        if (estado_deseado == True and cont.status == "exited"):
                            cont.start()
                            msg = f"[+] Contenedor '{container.name}' iniciado."
                            print(msg)
                            log_file.write(f"{msg}\n")
                        elif (estado_deseado == False and cont.status == "running"):
                            cont.stop()
                            msg = f"[-] Contenedor '{container.name}' detenido."
                            print(msg)
                            log_file.write(f"{msg}\n")
            except Exception as e:
                print(f"EXECUTE_ERROR Docker: {e}")
                log_file.write(f"[❌] ERROR Docker: {e}\n")

        
        # --- EJECUCIÓN CUÁNTICA ADAPTATIVA ---
        if contenedores.get("hqc") == True:
            print("EXECUTE: HQC activo. Orquestando carga de trabajo cuántica...")
            
            algoritmo_qaoa_activo = contenedores.get("qaoa") == True
            algoritmo_vqe_activo = contenedores.get("vqe") == True

            if algoritmo_qaoa_activo or algoritmo_vqe_activo:
                try:
                    backend_key = next(b for b in ["qiskit_simulator", "cirq_simulator"] if contenedores.get(b))
                    algoritmo = "QAOA" if algoritmo_qaoa_activo else "VQE"
                    backend_nombre = backend_key.replace("_", " ").title()

                    # --- WORKLOAD ADAPTATION (Protección de Recursos) ---
                    cp = self._reglaAdaptacion_CP
                    
                    # NUEVA LÓGICA DE ESCALADO (Para ver variabilidad visual)
                    # HQC solo se enciende si CP > 100.
                    
                    # Nivel 1: Complejidad Media (100 - 250) -> 3 Ciudades (9 Qubits)
                    if cp < 250:
                        problem_size = 3
                    # Nivel 2: Complejidad Alta (> 250) -> 4 Ciudades (16 Qubits)
                    else:
                        problem_size = 4 

                    # Profundidad dinámica
                    # Nivel 1: Rápido (CP < 400)
                    circuit_depth = 1
                    # Nivel 2: Preciso (CP >= 400)
                    if cp >= 400:
                        circuit_depth = 2
                    
                    print(f"   >>> ADAPTACIÓN DE CARGA: CP={cp} detectado.")
                    print(f"   >>> ESTRATEGIA: Escalar a {problem_size} ciudades, Profundidad {circuit_depth}.")

                    backend_adapter = hqc_module.get_backend_adapter(backend_nombre)

                    if backend_adapter:
                        unique_id = f"{app_globals.escenario_activo_id}_{int(time.time())}"
                        params = {
                            "problema_id": unique_id,
                            "complejidad_cp": cp,
                            "size": problem_size,    
                            "depth": circuit_depth   
                        }
                        
                        print(f"EXECUTE: Enviando trabajo a {backend_nombre}...")
                        resultado = backend_adapter.execute_job(algoritmo=algoritmo, params=params)
                        
                        print(f"EXECUTE: Trabajo finalizado. Costo: {resultado.get('costo_optimo')}")
                        with open(log_path, "a", encoding="utf-8") as log_file:
                             log_file.write(f"[⚛️] Job HQC ({algoritmo} en {backend_nombre}): N={problem_size}, Depth={circuit_depth}, Costo={resultado.get('costo_optimo')}\n")
                    else:
                        print(f"EXECUTE_ERROR: Sin adaptador para {backend_nombre}")

                except StopIteration:
                    print("EXECUTE_ERROR: HQC activo sin backend seleccionado.")
                except Exception as e:
                    print(f"EXECUTE_ERROR HQC: {e}")
            else:
                print("EXECUTE: HQC activo pero sin algoritmo seleccionado.")
        else:
            print("EXECUTE: HQC inactivo (Ahorro de energía).")

    def conocimiento(self, configuracion, mc, ica, complejidad_problema):
        """ Paso 5: CONOCIMIENTO """
        print("KNOWLEDGE: Actualizando base de conocimiento y estado global.")
        self._puntoVariacion = punto_variacion.PuntoVariacion(configuracion, mc, "gestor_aire")

    def getConocimiento(self):
        return self._puntoVariacion

    def getReglaAdaptacion(self):
        # --- NUEVO: Devolvemos también el razonamiento ---
        return {
            "calidad_aire_ica": self._reglaAdaptacion_ICA,
            "complejidad_problema_cp": self._reglaAdaptacion_CP,
            "prioridad_sla": self._reglaAdaptacion_SLA,
            "razonamiento": self._razonamiento_actual 
        }