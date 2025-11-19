# app/core/mapek.py (Versión Corregida con Lógica de Priorización)

import random
import docker
import datetime
import os

# --- INICIO DE MODIFICACIÓN DE IMPORTS ---
# Imports relativos para módulos en el mismo paquete (core)
from . import punto_variacion
# Imports absolutos para módulos en otros paquetes (services)
from app.services import agente_llm
from app.services import hqc_module # <--- AHORA ES LA FÁBRICA
from app import app_path # Importamos la ruta raíz del backend
# --- FIN DE MODIFICACIÓN DE IMPORTS ---


class Mapek:
    def __init__(self):
        self._puntoVariacion = None
        # Almacenamos ambas reglas por separado
        self._reglaAdaptacion_ICA = None 
        self._reglaAdaptacion_CP = None
        self._reglaAdaptacion_SLA = None # Nueva regla para guardar en el log

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
        Paso 1: MONITOREAR (Lógica de Tesis Combinada con Trade-off)
        """
        # 1. Sensores de Entorno Físico
        ica_simulado = random.choice([50, 150, 250])
        cp_simulado = random.choice([10, 350])
        
        # 2. Sensor de Política de Negocio (NUEVO)
        # Esto simula que el usuario a veces quiere respuesta ya (RAPIDEZ)
        # y a veces necesita el cálculo exacto (PRECISION).
        prioridad_negocio = random.choice(["RAPIDEZ", "PRECISION"])

        print(f"\n🔎 MONITOR: Contexto Detectado")
        print(f"   - Calidad Aire (ICA): {ica_simulado}")
        print(f"   - Complejidad (CP):   {cp_simulado}")
        print(f"   - Prioridad SLA:      {prioridad_negocio} <--- Clave para la decisión")
        
        # Guardar reglas para el log
        self._reglaAdaptacion_ICA = ica_simulado
        self._reglaAdaptacion_CP = cp_simulado
        self._reglaAdaptacion_SLA = prioridad_negocio # Guardamos para el log
        
        # Pasamos la prioridad al análisis
        self.analizar(mc, ica_simulado, cp_simulado, prioridad_negocio)

    def analizar(self, mc, ica, complejidad_problema, prioridad):
        """
        Paso 2: ANALIZAR (usando el Agente LLM con Prompt Mejorado)
        """
        print(f"🧠 ANALYZE: Razonando configuración óptima con prioridad {prioridad}...")
        
        reglas_del_modelo = mc.exportar_reglas_texto()
        metricas_nisq = hqc_module.monitor_backends()
        
        # --- INICIO DE MODIFICACIÓN DEL PROMPT ---
        contexto_actual = f"""
        DATOS DEL ENTORNO:
        1. Calidad del Aire (ICA) = {ica}. 
           (Regla de negocio: Si ICA > 100, se deben priorizar ambientes cerrados y evitar deportes).
        
        2. Complejidad del Problema (CP) = {complejidad_problema}. 
           (Regla de negocio: Si CP > 300, 'Optimizacion de rutas' DEBE activarse y usar 'HQC'. Si CP es menor, 'HQC' debe estar inactivo).

        3. Prioridad del Momento (SLA) = {prioridad}.
           - Si es RAPIDEZ: Debes elegir el backend con MENOR tiempo de cola (queue_time_sec).
           - Si es PRECISION: Debes elegir el backend con MENOR tasa de error (error_rate).

        4. Estado de los Backends Cuánticos:
           {metricas_nisq} 
        """
        # --- FIN DE MODIFICACIÓN DEL PROMPT ---
        
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
        
        # Llamar a conocimiento() ANTES de planificar()
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
        """ Paso 4: EJECUTAR (Ahora usando la Fábrica HQC y el trigger correcto) """
        
        # Añadir comprobación de seguridad
        if contenedores is None:
            print("EXECUTE: Plan de contenedores vacío. Omitiendo ejecución.")
            return

        client = docker.from_env()
        print("EXECUTE: Iniciando ejecución de contenedores Docker...")
        
        log_path = os.path.join(app_path, "data", "cambios.log")
        with open(log_path, "a", encoding="utf-8") as log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"\n--- RECONFIGURACIÓN a las {timestamp} ---\n")
            log_file.write(f"Regla de Adaptación (ICA): {self._reglaAdaptacion_ICA}\n")
            log_file.write(f"Regla de Adaptación (CP): {self._reglaAdaptacion_CP}\n")
            # Registrar la nueva regla SLA
            log_file.write(f"Regla de Adaptación (SLA): {self._reglaAdaptacion_SLA}\n")
            
            try:
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
            except Exception as e:
                print(f"EXECUTE_ERROR: Fallo al interactuar con Docker. ¿Está corriendo? Error: {e}")
                log_file.write(f"[❌] ERROR Docker: {e}\n")

        
        # --- INICIO DE MODIFICACIÓN DE EJECUCIÓN CUÁNTICA ---
        
        # --- Ejecución Cuántica ---
        if contenedores.get("hqc") == True:
            print("EXECUTE: HQC está activo. Verificando trabajo cuántico...")
            
            # El trigger es que un algoritmo (QAOA o VQE) esté activo.
            algoritmo_qaoa_activo = contenedores.get("qaoa") == True
            algoritmo_vqe_activo = contenedores.get("vqe") == True

            if algoritmo_qaoa_activo or algoritmo_vqe_activo:
                try:
                    # 1. Obtener las decisiones del LLM (del plan)
                    backend_activo_key = next(b for b in ["qiskit_simulator", "cirq_simulator"] if contenedores.get(b))
                    
                    # Determinar el algoritmo (ya lo sabemos, pero lo confirmamos)
                    algoritmo_activo = "QAOA" if algoritmo_qaoa_activo else "VQE"
                    
                    backend_nombre_formal = backend_activo_key.replace("_", " ").title()

                    print(f"EXECUTE: Delegando trabajo cuántico -> Algoritmo: {algoritmo_activo}, Backend: {backend_nombre_formal}")
                    
                    # 2. Usar la FÁBRICA de HQC para obtener el adaptador correcto
                    backend_adapter = hqc_module.get_backend_adapter(backend_nombre_formal)

                    if backend_adapter:
                        # 3. Ejecutar el trabajo usando la interfaz estándar
                        params = {"problema_id": "ruta_123", "complejidad": self._reglaAdaptacion_CP} 
                        resultado_cuantico = backend_adapter.execute_job(algoritmo=algoritmo_activo, params=params)
                        
                        print(f"EXECUTE: Resultado cuántico recibido: {resultado_cuantico}")
                        with open(log_path, "a", encoding="utf-8") as log_file:
                             log_file.write(f"[⚛️] Trabajo cuántico ({algoritmo_activo} en {backend_nombre_formal}) ejecutado.\n")
                    else:
                        msg = f"No se encontró un adaptador para el backend '{backend_nombre_formal}'."
                        print(f"EXECUTE_ERROR: {msg}")
                        with open(log_path, "a", encoding="utf-8") as log_file:
                            log_file.write(f"[❌] ERROR HQC: {msg}\n")

                except StopIteration:
                    print("EXECUTE_ERROR: HQC activo, pero no se encontró backend válido en el plan.")
                except Exception as e:
                    print(f"EXECUTE_ERROR: Falla inesperada en la ejecución cuántica. Error: {e}")
            
            else:
                # Esto pasará si el LLM activa 'hqc' pero no 'qaoa' ni 'vqe' (lo cual violaría el XOR)
                print("EXECUTE: HQC activo, pero ningún algoritmo (QAOA/VQE) fue seleccionado. En espera.")
        else:
            print("EXECUTE: HQC está inactivo. Omitiendo ejecución cuántica.")

    # --- FIN DE MODIFICACIÓN DE EJECUCIÓN CUÁNTICA ---

    def conocimiento(self, configuracion, mc, ica, complejidad_problema):
        """ Paso 5: CONOCIMIENTO """
        print("KNOWLEDGE: Actualizando Punto de Variación.")
        self._puntoVariacion = punto_variacion.PuntoVariacion(configuracion, mc, "gestor_aire")
        # Los valores de las reglas ya se establecieron en monitoreo()

    def getConocimiento(self):
        return self._puntoVariacion

    def getReglaAdaptacion(self):
        return {
            "calidad_aire_ica": self._reglaAdaptacion_ICA,
            "complejidad_problema_cp": self._reglaAdaptacion_CP,
            "prioridad_sla": self._reglaAdaptacion_SLA # Agregado al estado global
        }