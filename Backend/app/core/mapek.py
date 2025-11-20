# app/core/mapek.py

import random
import docker
import datetime
import os

# --- IMPORTS ---
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

    def _find_features_in_json(self, data: dict) -> dict:
        """ Recorre un JSON y extrae claves con valores booleanos. """
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
        """ Valida que la configuración respete las reglas del Feature Model. """
        print("VALIDATE: Verificando la configuración del LLM...")
        
        # 1. Validar 'Requiere'
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

        # 2. Validar Jerarquía (Padre-Hijo, XOR, OR, Obligatoria)
        for c in mc.caracteristicas:
            nombre_padre = c.getNombre.replace(" ", "_").lower()
            
            if config_dict.get(nombre_padre) == True:
                hijos_xor = [r[0].replace(" ", "_").lower() for r in c.getRelaciones if r[1] == "XOR"]
                hijos_or = [r[0].replace(" ", "_").lower() for r in c.getRelaciones if r[1] == "OR"]

                # Obligatoria
                for rel in c.getRelaciones:
                    if rel[1] == "Obligatoria":
                        hijo_key = rel[0].replace(" ", "_").lower()
                        if not config_dict.get(hijo_key):
                            print(f"VALIDATE_ERROR: Regla 'Obligatoria' violada en '{nombre_padre}'.")
                            return False
                
                # XOR
                if hijos_xor:
                    activos_xor = sum(1 for h in hijos_xor if config_dict.get(h) == True)
                    if activos_xor != 1:
                        print(f"VALIDATE_ERROR: Regla 'XOR' violada en '{nombre_padre}'. Activos: {activos_xor}")
                        return False
                
                # OR
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
                            print(f"VALIDATE_ERROR: Jerarquía violada. Padre '{nombre_padre}' inactivo, hijo '{hijo_key}' activo.")
                            return False

        print("VALIDATE: Configuración del LLM es VÁLIDA.")
        return True

    def monitoreo(self, mc):
        """ Paso 1: MONITOREAR """
        ica_simulado = random.choice([50, 150, 250])
        cp_simulado = random.choice([10, 350])
        prioridad_negocio = random.choice(["RAPIDEZ", "PRECISION"])

        print(f"\n🔎 MONITOR: Contexto Detectado")
        print(f"   - Calidad Aire (ICA): {ica_simulado}")
        print(f"   - Complejidad (CP):   {cp_simulado}")
        print(f"   - Prioridad SLA:      {prioridad_negocio}")
        
        self._reglaAdaptacion_ICA = ica_simulado
        self._reglaAdaptacion_CP = cp_simulado
        self._reglaAdaptacion_SLA = prioridad_negocio
        
        self.analizar(mc, ica_simulado, cp_simulado, prioridad_negocio)

    def analizar(self, mc, ica, complejidad_problema, prioridad):
        """ Paso 2: ANALIZAR """
        print(f"🧠 ANALYZE: Razonando configuración óptima con prioridad {prioridad}...")
        
        reglas_del_modelo = mc.exportar_reglas_texto()
        metricas_nisq = hqc_module.monitor_backends()
        
        contexto_actual = f"""
        DATOS DEL ENTORNO:
        1. Calidad del Aire (ICA) = {ica}. 
           (Regla: Si ICA > 100, priorizar ambientes cerrados).
        
        2. Complejidad del Problema (CP) = {complejidad_problema}. 
           (Regla: Si CP > 300, 'Optimizacion de rutas' DEBE activarse y usar 'HQC'. Si CP es menor, 'HQC' debe estar inactivo).

        3. Prioridad (SLA) = {prioridad}.
           - RAPIDEZ: Elegir backend con MENOR cola.
           - PRECISION: Elegir backend con MENOR error.

        4. Estado Backends:
           {metricas_nisq} 
        """
        
        config_dict_llm = agente_llm.obtener_configuracion_llm(contexto_actual, reglas_del_modelo)

        if not config_dict_llm:
            print("ANALYZE_ERROR: Configuración vacía del LLM.")
            return 

        config_plana = self._find_features_in_json(config_dict_llm)
        print(f"ANALYZE: Configuración plana: {config_plana}")

        # Validación
        config_plana_con_raiz = config_plana.copy()
        config_plana_con_raiz['gestor_aire'] = True 
        
        if not self._validar_configuracion(config_plana_con_raiz, mc):
            print("ANALYZE_ERROR: Configuración INVÁLIDA.")
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

        print(f"ANALYZE: Configuración final aceptada: {configuracion_final}")
        
        self.conocimiento(configuracion_final, mc, ica, complejidad_problema)
        self.planificar()

    def planificar(self):
        """ Paso 3: PLANIFICAR """
        if self._puntoVariacion is None:
            print("PLAN: No hay Punto de Variación válido.")
            return

        contenedores = self._puntoVariacion.obtenerConfiguracion()
        print(f"PLAN: Plan Docker listo: {contenedores}")
        self.ejecutar(contenedores)

    def ejecutar(self, contenedores):
        """ Paso 4: EJECUTAR (Con Adaptación de Carga de Trabajo Cuántica) """
        
        if contenedores is None:
            print("EXECUTE: Plan vacío.")
            return

        client = docker.from_env()
        print("EXECUTE: Reconfigurando Docker...")
        
        log_path = os.path.join(app_path, "data", "cambios.log")
        with open(log_path, "a", encoding="utf-8") as log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"\n--- RECONFIGURACIÓN {timestamp} ---\n")
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
            print("EXECUTE: HQC activo. Analizando parámetros de trabajo...")
            
            algoritmo_qaoa_activo = contenedores.get("qaoa") == True
            algoritmo_vqe_activo = contenedores.get("vqe") == True

            if algoritmo_qaoa_activo or algoritmo_vqe_activo:
                try:
                    backend_key = next(b for b in ["qiskit_simulator", "cirq_simulator"] if contenedores.get(b))
                    algoritmo = "QAOA" if algoritmo_qaoa_activo else "VQE"
                    backend_nombre = backend_key.replace("_", " ").title()

                    # --- NUEVA LÓGICA: Mapeo de Complejidad (CP) a Configuración Cuántica ---
                    cp = self._reglaAdaptacion_CP
                    
                    # Definir Tamaño del Problema (Qubits/Ciudades)
                    # AJUSTE DE SEGURIDAD: Limitamos a máximo 4 ciudades (16 qubits)
                    # para evitar crash por falta de RAM con 5 ciudades (25 qubits).
                    
                    if cp < 100:
                        problem_size = 3  # 9 Qubits (Rápido)
                    else:
                        # Para cualquier CP medio/alto, usamos 4 ciudades.
                        # 16 Qubits es suficiente para demostrar alta carga sin colapsar Docker.
                        problem_size = 4 

                    # Definir Profundidad del Circuito (Capas/Reps)
                    # Mantenemos la profundidad dinámica, eso impacta CPU pero menos memoria
                    circuit_depth = 1
                    if cp > 200:
                        circuit_depth = 2
                    
                    print(f"   >>> WORKLOAD ADAPTATION (SAFE): CP={cp} -> Tamaño={problem_size}, Profundidad={circuit_depth}")

                    # Instanciar adaptador
                    backend_adapter = hqc_module.get_backend_adapter(backend_nombre)

                    if backend_adapter:
                        # Pasamos los parámetros dinámicos
                        params = {
                            "problema_id": f"job_auto_{cp}",
                            "complejidad_cp": cp,
                            "size": problem_size,    # Nro de Ciudades o Nodos
                            "depth": circuit_depth   # Repeticiones del ansatz
                        }
                        
                        print(f"EXECUTE: Enviando trabajo a {backend_nombre} ({algoritmo})...")
                        resultado = backend_adapter.execute_job(algoritmo=algoritmo, params=params)
                        
                        print(f"EXECUTE: Resultado: {resultado}")
                        with open(log_path, "a", encoding="utf-8") as log_file:
                             log_file.write(f"[⚛️] Job HQC ({algoritmo} en {backend_nombre}): Tamaño={problem_size}, Depth={circuit_depth}\n")
                    else:
                        print(f"EXECUTE_ERROR: Sin adaptador para {backend_nombre}")

                except StopIteration:
                    print("EXECUTE_ERROR: HQC activo sin backend seleccionado.")
                except Exception as e:
                    print(f"EXECUTE_ERROR HQC: {e}")
            else:
                print("EXECUTE: HQC activo pero sin algoritmo seleccionado.")
        else:
            print("EXECUTE: HQC inactivo.")

    def conocimiento(self, configuracion, mc, ica, complejidad_problema):
        """ Paso 5: CONOCIMIENTO """
        print("KNOWLEDGE: Actualizando Punto de Variación.")
        self._puntoVariacion = punto_variacion.PuntoVariacion(configuracion, mc, "gestor_aire")

    def getConocimiento(self):
        return self._puntoVariacion

    def getReglaAdaptacion(self):
        return {
            "calidad_aire_ica": self._reglaAdaptacion_ICA,
            "complejidad_problema_cp": self._reglaAdaptacion_CP,
            "prioridad_sla": self._reglaAdaptacion_SLA
        }