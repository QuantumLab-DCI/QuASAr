import random
import punto_variacion
import docker
import datetime
import hqc_module
import agente_llm  # <--- NUEVA IMPORTACIÓN
# import aprendizaje_automatico <-- ELIMINADO

class Mapek:
    def __init__(self):
        self._puntoVariacion = None
        # Almacenamos ambas reglas por separado
        self._reglaAdaptacion_ICA = None 
        self._reglaAdaptacion_CP = None

    # --- INICIO DE NUEVA FUNCIÓN ---
    def _find_features_in_json(self, data: dict) -> dict:
        """
        Recorre un JSON (potencialmente anidado) y extrae todas
        las claves que tengan un valor booleano (true/false).
        Esto nos protege si el LLM envía un árbol en lugar de un JSON plano.
        """
        features = {}
        if isinstance(data, dict):
            for k, v in data.items():
                key_normalizada = k.replace(" ", "_").lower()
                if isinstance(v, bool):
                    features[key_normalizada] = v
                elif isinstance(v, dict):
                    # Si es un dict anidado, buscar dentro
                    features.update(self._find_features_in_json(v))
        return features
    # --- FIN DE NUEVA FUNCIÓN ---

    # --- INICIO DE NUEVA FUNCIÓN DE VALIDACIÓN ---
    def _validar_configuracion(self, config_dict: dict, mc) -> bool:
        """
        Valida que el JSON plano del LLM respete las reglas del Feature Model.
        """
        print("VALIDATE: Verificando la configuración del LLM...")
        
        # 1. Obtener todas las reglas 'Requiere'
        reglas_requiere = []
        for c in mc.caracteristicas:
            for rel in c.getRelaciones:
                if rel[1] == "Requiere":
                    req_key = c.getNombre.replace(" ", "_").lower()
                    req_val = rel[0].replace(" ", "_").lower()
                    reglas_requiere.append((req_key, req_val))

        # 2. Validar las reglas 'Requiere' globales
        for (quien_requiere, quien_es_requerido) in reglas_requiere:
            if config_dict.get(quien_requiere) and not config_dict.get(quien_es_requerido):
                print(f"VALIDATE_ERROR: Regla 'Requiere' violada. '{quien_requiere}' está activo pero '{quien_es_requerido}' está inactivo.")
                return False

        # 3. Validar la jerarquía (Padre-Hijo)
        for c in mc.caracteristicas:
            nombre_padre = c.getNombre.replace(" ", "_").lower()
            
            # Si el padre está ACTIVO, sus hijos deben cumplir las reglas
            if config_dict.get(nombre_padre) == True:
                hijos_xor = [r[0].replace(" ", "_").lower() for r in c.getRelaciones if r[1] == "XOR"]
                hijos_or = [r[0].replace(" ", "_").lower() for r in c.getRelaciones if r[1] == "OR"]

                # Regla Obligatoria
                for rel in c.getRelaciones:
                    if rel[1] == "Obligatoria":
                        hijo_key = rel[0].replace(" ", "_").lower()
                        if not config_dict.get(hijo_key):
                            print(f"VALIDATE_ERROR: Regla 'Obligatoria' violada. Padre '{nombre_padre}' activo, pero hijo '{hijo_key}' inactivo.")
                            return False
                
                # Regla XOR
                if hijos_xor:
                    activos_xor = sum(1 for h in hijos_xor if config_dict.get(h) == True)
                    if activos_xor != 1:
                        print(f"VALIDATE_ERROR: Regla 'XOR' violada. Padre '{nombre_padre}' activo, pero el grupo no tiene 1 hijo activo (tiene {activos_xor}).")
                        return False
                
                # Regla OR
                if hijos_or:
                    activos_or = sum(1 for h in hijos_or if config_dict.get(h) == True)
                    if activos_or == 0:
                        print(f"VALIDATE_ERROR: Regla 'OR' violada. Padre '{nombre_padre}' activo, pero el grupo no tiene hijos activos.")
                        return False
            
            # Si el padre está INACTIVO, todos sus hijos (excepto 'Requiere') deben estar inactivos
            elif config_dict.get(nombre_padre) == False:
                 for rel in c.getRelaciones:
                    if rel[1] != "Requiere": # Las reglas 'Requiere' no son jerárquicas
                        hijo_key = rel[0].replace(" ", "_").lower()
                        if config_dict.get(hijo_key) == True:
                            print(f"VALIDATE_ERROR: Regla de Jerarquía violada. Padre '{nombre_padre}' inactivo, pero hijo '{hijo_key}' activo.")
                            return False

        print("VALIDATE: Configuración del LLM es VÁLIDA.")
        return True
    # --- FIN DE NUEVA FUNCIÓN DE VALIDACIÓN ---

    def monitoreo(self, mc):
        """
        Paso 1: MONITOREAR (Lógica de Tesis Combinada)
        """
        ica_simulado = random.choice([50, 150, 250])
        print(f"MONITOR (Clásico): Calidad del Aire (ICA) detectada: {ica_simulado}")
        cp_simulado = random.choice([10, 350])
        print(f"MONITOR (Cuántico): Complejidad de Problema (CP) detectada: {cp_simulado}")
        self.analizar(mc, ica_simulado, cp_simulado)

    def analizar(self, mc, ica, complejidad_problema):
        """
        Paso 2: ANALIZAR (usando el Agente LLM)
        """
        print(f"ANALYZE: Iniciando análisis con ICA={ica} y CP={complejidad_problema}")
        
        reglas_del_modelo = mc.exportar_reglas_texto()
        metricas_nisq = hqc_module.monitor_backends()
        contexto_actual = f"""
        - Calidad del Aire (ICA) = {ica}. 
          (Regla de negocio: Si ICA > 100, se deben priorizar ambientes cerrados y evitar deportes).
        - Complejidad del Problema (CP) = {complejidad_problema}. 
          (Regla de negocio: Si CP > 300, HQC debe estar activo. Si es menor, HQC debe estar inactivo).
        - Métricas NISQ: {metricas_nisq} 
          (Regla de negocio: Usar para elegir el *mejor* backend HQC (menor cola+error) si HQC se activa).
        """
        
        config_dict_llm = agente_llm.obtener_configuracion_llm(
            contexto_actual, 
            reglas_del_modelo
        )

        if not config_dict_llm:
            print("ANALYZE_ERROR: El LLM devolvió una configuración vacía. Omitiendo ciclo.")
            return 

        config_plana = self._find_features_in_json(config_dict_llm)
        print(f"ANALYZE: Configuración plana parseada: {config_plana}")

        # --- INICIO DE VALIDACIÓN ---
        # Añadir 'gestor_aire: True' para que la validación funcione
        # ya que el LLM no lo incluye (porque siempre está activo)
        config_plana_con_raiz = config_plana.copy()
        config_plana_con_raiz['gestor_aire'] = True 
        
        if not self._validar_configuracion(config_plana_con_raiz, mc):
            print("ANALYZE_ERROR: La configuración del LLM es INVÁLIDA. Omitiendo ciclo.")
            return
        # --- FIN DE VALIDACIÓN ---

        configuracion_final = []
        for key, value in config_plana.items(): 
            nombre_formal = next(
                (c.getNombre for c in mc.caracteristicas 
                 if c.getNombre.replace(" ", "_").lower() == key.lower()), 
                key.replace("_", " ").capitalize()
            )
            estado = "activada" if value else "desactivada"
            configuracion_final.append(f"{nombre_formal} {estado}")

        print(f"ANALYZE: Configuración final (VÁLIDA) decidida por el LLM: {configuracion_final}")
        
        self.conocimiento(configuracion_final, mc, ica, complejidad_problema)
        self.planificar() 

    def planificar(self):
        """ Paso 3: PLANIFICAR """
        if self._puntoVariacion is None:
            print("PLAN: No hay Punto de Variación válido. Omitiendo planificación.")
            return

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
                estado_deseado = contenedores.get(container.name)
                if estado_deseado is not None:
                    cont = client.containers.get(container.id)
                    if (estado_deseado == True and cont.status == "exited"):
                        cont.start()
                        mensaje = f"Contenedor '{container.name}' iniciado."
                        print(f"[+] {mensaje}")
                        log_file.write(f"[+] {mensaje}\n")
                    elif (estado_deseado == False and cont.status == "running"):
                        cont.stop()
                        mensaje = f"Contenedor '{container.name}' detenido."
                        print(f"[-] {mensaje}")
                        log_file.write(f"[-] {mensaje}\n")
        
        # --- Ejecución Cuántica ---
        if contenedores.get("hqc") == True:
            print("EXECUTE: HQC está activo. Verificando trabajo cuántico...")
            if contenedores.get("optimizacion_de_rutas") == True:
                try:
                    backend_activo = next(b for b in ["qiskit_simulator", "spinq_simulator", "tql_simulator"] if contenedores.get(b))
                    algoritmo_activo = next(a.upper() for a in ["qaoa", "vqe"] if contenedores.get(a))
                    backend_nombre_formal = backend_activo.replace("_", " ").title()
                    print(f"EXECUTE: Delegando trabajo cuántico -> Algoritmo: {algoritmo_activo}, Backend: {backend_nombre_formal}")
                    params = {"problema_id": "ruta_123", "complejidad": self._reglaAdaptacion_CP} 
                    resultado_cuantico = hqc_module.ejecutar_quantum_job(algoritmo=algoritmo_activo, backend=backend_nombre_formal, params=params)
                    print(f"EXECUTE: Resultado cuántico recibido: {resultado_cuantico}")
                    with open("cambios.log", "a", encoding="utf-8") as log_file:
                         log_file.write(f"[⚛️] Trabajo cuántico ({algoritmo_activo} en {backend_nombre_formal}) ejecutado.\n")
                except StopIteration:
                    print("EXECUTE_ERROR: HQC activo, pero no se encontró backend o algoritmo válido en el plan.")
            else:
                print("EXECUTE: HQC activo, pero 'optimizacion_de_rutas' no. En espera.")
        else:
            print("EXECUTE: HQC está inactivo. Omitiendo ejecución cuántica.")

    def conocimiento(self, configuracion, mc, ica, complejidad_problema):
        """ Paso 5: CONOCIMIENTO """
        self._puntoVariacion = punto_variacion.PuntoVariacion(configuracion, mc, "gestor_aire")
        self._reglaAdaptacion_ICA = ica
        self._reglaAdaptacion_CP = complejidad_problema

    def getConocimiento(self):
        return self._puntoVariacion

    def getReglaAdaptacion(self):
        return {
            "calidad_aire_ica": self._reglaAdaptacion_ICA,
            "complejidad_problema_cp": self._reglaAdaptacion_CP
        }