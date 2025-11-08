import itertools
import numpy as np
import csv

class Nodo:
    def __init__(self, nombre):
        self._nombre = nombre
        self._relaciones = []

    def agregarRelacion(self, nodo):
        self._relaciones.append(nodo)

    @property
    def getNombre(self):
        return self._nombre

    @property
    def getRelaciones(self):
        return self._relaciones

class ModeloCaracteristicas:
    def __init__(self):
        self.caracteristicas = []

    def agregarCaracteristica(self, nodo):
        self.caracteristicas.append(nodo)

    def relacionar(self, nodo1, nodo2, tipoRelacion):
        nodo1.agregarRelacion([nodo2.getNombre,tipoRelacion])
        #nodo2.agregarRelacion([nodo1])

    def buscarCaracteristica(self, nombreCaracteristica):
        for rama in self.caracteristicas:
            if(rama.getNombre == nombreCaracteristica):
                return rama
        return None
    
    def buscarCaracteristicaPadre(self, nombreCaracteristica, nombreRelacion):
        for rama in self.caracteristicas:
            for relaciones in rama.getRelaciones:
                if(relaciones == [nombreCaracteristica,nombreRelacion]):
                    return rama
        return None

    def calcularPosiblesEstados(self):
        reconfiguraciones = []
        for nodo in self.caracteristicas:
            for relacion in nodo.getRelaciones:
                posibleEstado = self.estadoTipoRelacion(relacion)
                if(posibleEstado != []):
                    reconfiguraciones.append(posibleEstado)
        return self.eliminarDuplicados(reconfiguraciones)

    def estadoTipoRelacion(self,nodo):
        nodoArbol = []
        if (nodo[1] == "Obligatoria"):
            # CORRECCIÓN: Debe generar AMBOS estados.
            # El filtro (removerRelacionesInvalidas) decidirá si es válido.
            nodoArbol.append([nodo[0] + " activada", nodo[0] + " desactivada"])
        if (nodo[1] == "Opcional"):
            nodoArbol.append([nodo[0] + " activada", nodo[0] + " desactivada"])
        if (nodo[1] == "XOR"):
            caracteristicas = self.buscarRelacionesXOR(nodo[0])
            for combo in itertools.product([True, False], repeat=len(caracteristicas)):
                
                # --- INICIO DE CORRECCIÓN (XOR) ---
                # Debe permitir 1 activo (para XOR) o 0 activos (para padre inactivo)
                if combo.count(True) == 1 or combo.count(True) == 0:
                    resultado = []
                    for i, activado in enumerate(combo):
                        estado = "activada" if activado else "desactivada"
                        resultado.append(f"{caracteristicas[i]} {estado}")
                    nodoArbol.append(resultado)
                # --- FIN DE CORRECCIÓN ---
                
        if (nodo[1] == "OR"):
            caracteristicas = self.buscarRelacionesOR(nodo[0])
            combinaciones = list(itertools.product(["activada", "desactivada"], repeat=len(caracteristicas)))
            # Filtrar las combinaciones para asegurarse de que al menos una posición esté activada
            combinaciones_filtradas = [combo for combo in combinaciones if combo.count("activada") >= 0]
            # Agregar el texto "activado" o "desactivado" a cada posición del arreglo en cada combinación
            combinaciones_con_texto = [[f"{caracteristicas[i]} {estado}" for i, estado in enumerate(combo)] for combo in
                                       combinaciones_filtradas]
            nodoArbol = combinaciones_con_texto
        return nodoArbol

    def buscarRelacionesXOR(self, nodo):
        caracteristicasXOR = []
        caracteristica = self.buscarCaracteristicaPadre(nodo, "XOR")
        for ramas in caracteristica.getRelaciones:
            if(ramas[1] == "XOR"):
                caracteristicasXOR.append(ramas[0])
        return caracteristicasXOR

    def buscarRelacionesOR(self, nodo):
        caracteristicasOR = []
        caracteristica = self.buscarCaracteristicaPadre(nodo, "OR")
        for ramas in caracteristica.getRelaciones:
            if (ramas[1] == "OR"):
                caracteristicasOR.append(ramas[0])
        return caracteristicasOR

    def removerRelacionesInvalidas(self, reconfiguraciones):
        posiblesEstados = []
        print("reconfiguraciones iniciales", len(reconfiguraciones))
        
        for nodo in reconfiguraciones:
            relacionInvalida = False
            
            # 1. Convertimos la fila en un diccionario para búsquedas fáciles
            config_dict = {}
            for item in nodo:
                if " activada" in item:
                    config_dict[item.replace(" activada", "")] = True
                elif " desactivada" in item:
                    config_dict[item.replace(" desactivada", "")] = False

            # --- INICIO DE CORRECCIÓN (Lógica del Nodo Raíz) ---
            #
            # El nodo raíz ("Gestor aire") está implícitamente ACTIVO.
            # Debemos validar a sus hijos obligatorios ANTES del bucle principal.
            #
            raiz_caracteristicaBuscada = self.buscarCaracteristica("Gestor aire")
            if raiz_caracteristicaBuscada:
                for relacion in raiz_caracteristicaBuscada.getRelaciones:
                    # REGLA: Si la raíz está activa, sus hijos OBLIGATORIOS deben estar ACTIVOS.
                    if relacion[1] == "Obligatoria" and config_dict.get(relacion[0]) == False:
                        relacionInvalida = True
                        # print(f"INVALIDADO (Raíz): Hijo Obligatorio '{relacion[0]}' está inactivo.")
                        break # Esta permutación es inválida
            
            if relacionInvalida:
                # Opcional: print(f"FILTRADO (Raíz): {nodo}")
                continue # Saltar al siguiente 'nodo' en reconfiguraciones
            #
            # --- FIN DE CORRECCIÓN ---


            # 2. Iteramos por las características HIJO (sin el hack de "Gestor aire")
            for nombre_caracteristica, estado_activo in config_dict.items():
                caracteristicaBuscada = self.buscarCaracteristica(nombre_caracteristica)
                
                # Si no se encuentra, es un nodo hoja (ej. "QAOA"), lo saltamos
                if caracteristicaBuscada is None:
                    continue

                # Encontrado: Es un nodo padre (ej. "HQC", "Backend", "Turismo")
                
                # REGLA 1: Si un padre está INACTIVO, sus hijos OBLIGATORIOS/XOR/OR deben estar INACTIVOS.
                if not estado_activo: # Si el padre (ej. HQC) está Falso (desactivado)
                    for relacion in caracteristicaBuscada.getRelaciones:
                        # Si un hijo (que no sea 'Requiere') está ACTIVO
                        if relacion[1] != "Requiere" and config_dict.get(relacion[0]) == True:
                            relacionInvalida = True
                            # print(f"INVALIDADO (Regla 1): Padre '{nombre_caracteristica}' inactivo, pero hijo '{relacion[0]}' activo.")
                            break # Salir del bucle de relaciones
                
                # REGLA 2: Si un padre está ACTIVO, sus hijos deben cumplir sus reglas.
                elif estado_activo: # Si el padre (ej. HQC) está Cierto (activado)
                    
                    # --- Lógica para OBLIGATORIA (Corregida) ---
                    for relacion in caracteristicaBuscada.getRelaciones:
                        if relacion[1] == "Obligatoria" and config_dict.get(relacion[0]) == False:
                            relacionInvalida = True
                            # print(f"INVALIDADO (Regla 2-Oblig): Padre '{nombre_caracteristica}' activo, pero hijo Obligatorio '{relacion[0]}' inactivo.")
                            break # Salir del bucle de relaciones
                    
                    if relacionInvalida:
                        break # Salir del bucle de características
                    
                    # --- Lógica de validación para XOR/OR ---
                    hijos_xor = [r[0] for r in caracteristicaBuscada.getRelaciones if r[1] == "XOR"]
                    hijos_or = [r[0] for r in caracteristicaBuscada.getRelaciones if r[1] == "OR"]

                    if hijos_xor:
                        # Si es un grupo XOR, DEBE tener exactamente 1 hijo activo
                        activos_xor = sum(1 for h in hijos_xor if config_dict.get(h) == True)
                        if activos_xor != 1:
                            relacionInvalida = True
                            # print(f"INVALIDADO (Regla 2-XOR): Padre '{nombre_caracteristica}' activo, pero grupo XOR no tiene 1 hijo activo.")
                            break

                    if hijos_or:
                        # Si es un grupo OR, DEBE tener AL MENOS 1 hijo activo
                        activos_or = sum(1 for h in hijos_or if config_dict.get(h) == True)
                        if activos_or == 0: 
                            relacionInvalida = True
                            # print(f"INVALIDADO (Regla 2-OR): Padre '{nombre_caracteristica}' activo, pero grupo OR no tiene hijos activos.")
                            break
                
                if relacionInvalida:
                    break # Salir del bucle de características

            if not relacionInvalida:
                posiblesEstados.append(nodo)
            # else:
                # Opcional: Descomenta esto para ver las filas que se están filtrando
                # print(f"FILTRADO: {nodo}") 

        print("reconfiguraciones finales sin excluir require", len(posiblesEstados))
        return self.filtrarRelacionesRequire(posiblesEstados)



    def filtrarRelacionesRequire(self, reconfiguraciones):
        posiblesEstados = []
        
        # 1. Encontrar todas las reglas "Requiere" del modelo
        reglas_requiere = []
        for caracteristica in self.caracteristicas:
            for relacion in caracteristica.getRelaciones:
                if relacion[1] == "Requiere":
                    # Guardamos la regla como (quien_requiere, quien_es_requerido)
                    # Ej: ('Optimizacion de rutas', 'HQC')
                    reglas_requiere.append((caracteristica.getNombre, relacion[0]))

        print(f"Reglas 'Requiere' detectadas: {reglas_requiere}")

        # 2. Iterar por cada configuración y validarla
        for nodo in reconfiguraciones:
            condicion_valida = True
            
            # Convertir la fila a un diccionario para búsquedas fáciles
            config_dict = {}
            for item in nodo:
                if " activada" in item:
                    config_dict[item.replace(" activada", "")] = True
                elif " desactivada" in item:
                    config_dict[item.replace(" desactivada", "")] = False
            
            # 3. Aplicar cada regla
            for (quien_requiere, quien_es_requerido) in reglas_requiere:
                
                # Esta es la única condición que invalida la fila:
                # Si el que requiere está ACTIVO, pero el requerido está INACTIVO
                if config_dict.get(quien_requiere) == True and config_dict.get(quien_es_requerido) == False:
                    condicion_valida = False
                    # print(f"FILTRADO: '{quien_requiere}' activo REQUIERE '{quien_es_requerido}' activo.")
                    break # Esta fila es inválida, no seguir revisando
            
            if condicion_valida:
                posiblesEstados.append(nodo)
        
        # Este número ahora debería ser 768
        print(f"reconfiguraciones finales (con 'Requiere' validado): {len(posiblesEstados)}")
        return posiblesEstados

    def ordenarPosiblesEstados(self, arrays):
        arr = []
        for array in arrays:
            array.sort()
            for subarray in array:
                subarray.sort()
        return arrays
    
    def buscarPosibleEstado(self, reconfiguraciones, nodo):
        condicion = False
        for rama in reconfiguraciones:
            for hoja in rama:
                if hoja == nodo:
                    condicion = True
                    return condicion
        return condicion

    def eliminarDuplicados(self, posiblesEstados):
        posiblesEstados = self.ordenarPosiblesEstados(posiblesEstados)
        print("posibles estados",len(posiblesEstados))
        # print(posiblesEstados) # Descomentado para no saturar la consola
        reconfiguraciones = []
        for rama in posiblesEstados:
            condicion = False
            for hoja in rama:
                condicion = self.buscarPosibleEstado(reconfiguraciones,hoja)
            if not condicion:
                if len(rama) == 1:
                    reconfiguraciones.append(hoja)
                else:
                    reconfiguraciones.append(rama)
        print("estados finales ",len(reconfiguraciones))
        # print(reconfiguraciones) # Descomentado para no saturar la consola
        return reconfiguraciones

    def buscarCaracteristicaOR(self, nodo):
        caracteristica = self.buscarCaracteristica(nodo)
        for ramas in caracteristica.getRelaciones:
            if (ramas[1] == "OR"):
                return ramas[0]
        return None



    def permutarCaracteristicas(self, reconfiguraciones):
        #result = list(set(itertools.product(*reconfiguraciones)))
        result = list(itertools.product(*reconfiguraciones))
        resultado = []
        print("largo tupla", len(result))
        for tupla in result:
            lista = list(tupla)
            arreglo = []
            for posicionLista in lista:
                if isinstance(posicionLista, list):
                    arreglo.extend(posicionLista)
                else:
                    arreglo.append(posicionLista)
            resultado.append(arreglo)
        print("cantidad resultados",len(resultado))
        return self.removerRelacionesInvalidas(resultado)

    def almacenarPosiblesEstados(self, nombreArchivo,resultado):
        with open(nombreArchivo, 'w', newline='') as archivo_csv:
            writer = csv.writer(archivo_csv)
            writer.writerows(resultado)

    def buscarPadre(self, caracteristica):
        for rama in self.caracteristicas:
            for relaciones in rama.getRelaciones:
                if(relaciones[0] == caracteristica):
                    return rama
        return None

    def obtenerArbol(self):
        arbol = []
        print("hola")
        for caracteristica in self.caracteristicas:
            arbol.append(caracteristica.getNombre)
            print(caracteristica.getNombre)
        return arbol

    def obtenerRelacionesCaracteristica(self, nombreCaracteristica):
        caracteristica = self.buscarCaracteristica(nombreCaracteristica)
        subCaracteristicas = []
        if caracteristica != None:
            for subCaracteristica in caracteristica.getRelaciones:
                subCaracteristicas.append(subCaracteristica[0])
        return subCaracteristicas

    def obtenerRelacionesCaracteristicaConRestriccion(self, nombreCaracteristica):
        caracteristica = self.buscarCaracteristica(nombreCaracteristica)
        subCaracteristicas = []
        if caracteristica != None:
            for subCaracteristica in caracteristica.getRelaciones:
                if subCaracteristica[1] != "Requiere" and subCaracteristica[1] != "Excluye":
                    subCaracteristicas.append(subCaracteristica[0])
        return subCaracteristicas
    
    def obtenerRelacionesMC(self):
        relacionesMC = {}
        for caracteristica in self.caracteristicas:
            relacionesCaracteristica = []
            for relacionCaracteristica in caracteristica.getRelaciones:
                if relacionCaracteristica[1] != "Requiere" and relacionCaracteristica[1] != "Excluye":
                    relacionesCaracteristica.append(relacionCaracteristica[0])
            relacionesMC.update({caracteristica.getNombre : relacionesCaracteristica})
        return relacionesMC

    #Entregar caracteristicas activas por subnivel
    #Ocupar POO para almacenar en local los puntos de variacion
    #Eliminar esta API
    #Caracteristica deberia tener el nombre, estado, dockerNombreContenedor


#class PuntoVariacion:
    




def generarPosiblesEstados():
    mc = ModeloCaracteristicas()
    mc.agregarCaracteristica(Nodo("Gestor aire"))
    mc.agregarCaracteristica(Nodo("Visualizador calidad de aire"))
    mc.agregarCaracteristica(Nodo("Visualizador restriccion uso lena"))
    mc.agregarCaracteristica(Nodo("Turismo"))
    mc.agregarCaracteristica(Nodo("Ambientes cerrados"))
    mc.agregarCaracteristica(Nodo("Ambientes abiertos"))
    mc.agregarCaracteristica(Nodo("Deportes"))
    mc.agregarCaracteristica(Nodo("Entretenimiento"))
    mc.agregarCaracteristica(Nodo("Entretenimiento familiar"))
    mc.agregarCaracteristica(Nodo("Entretenimiento adulto"))
    mc.agregarCaracteristica(Nodo("Entretenimiento tercera edad"))

        # --- INICIO DE TU MODIFICACIÓN ---
    mc.agregarCaracteristica(Nodo("HQC")) # El nodo principal
    mc.agregarCaracteristica(Nodo("Backend"))
    mc.agregarCaracteristica(Nodo("Algoritmo"))

    # Backends (ejemplo con 3)
    mc.agregarCaracteristica(Nodo("Qiskit Simulator"))
    mc.agregarCaracteristica(Nodo("SpinQ Simulator"))
    mc.agregarCaracteristica(Nodo("TQL Simulator"))

    # Algoritmos (ejemplo con 2)
    mc.agregarCaracteristica(Nodo("QAOA"))
    mc.agregarCaracteristica(Nodo("VQE"))

    # Tu nueva funcionalidad clásica que usará el HQC
    mc.agregarCaracteristica(Nodo("Optimizacion de rutas"))
    # --- FIN DE TU MODIFICACIÓN ---

    mc.relacionar(mc.buscarCaracteristica("Gestor aire"),mc.buscarCaracteristica("Visualizador calidad de aire"), "Obligatoria")
    mc.relacionar(mc.buscarCaracteristica("Gestor aire"), mc.buscarCaracteristica("Turismo"), "Obligatoria")
    mc.relacionar(mc.buscarCaracteristica("Gestor aire"), mc.buscarCaracteristica("Deportes"), "Opcional")
    mc.relacionar(mc.buscarCaracteristica("Gestor aire"), mc.buscarCaracteristica("Entretenimiento"), "Opcional")
    mc.relacionar(mc.buscarCaracteristica("Visualizador calidad de aire"), mc.buscarCaracteristica("Visualizador restriccion uso lena"), "Opcional")
    mc.relacionar(mc.buscarCaracteristica("Turismo"), mc.buscarCaracteristica("Ambientes cerrados"), "XOR")
    mc.relacionar(mc.buscarCaracteristica("Turismo"), mc.buscarCaracteristica("Ambientes abiertos"), "XOR")
    mc.relacionar(mc.buscarCaracteristica("Ambientes abiertos"), mc.buscarCaracteristica("Deportes"), "Requiere")
    mc.relacionar(mc.buscarCaracteristica("Ambientes cerrados"), mc.buscarCaracteristica("Visualizador restriccion uso lena"), "Requiere")
    mc.relacionar(mc.buscarCaracteristica("Entretenimiento"), mc.buscarCaracteristica("Entretenimiento familiar"), "OR")
    mc.relacionar(mc.buscarCaracteristica("Entretenimiento"), mc.buscarCaracteristica("Entretenimiento adulto"), "OR")
    mc.relacionar(mc.buscarCaracteristica("Entretenimiento"), mc.buscarCaracteristica("Entretenimiento tercera edad"), "OR")
    # --- INICIO DE TU MODIFICACIÓN ---
    # 1. HQC es opcional y depende de Gestor aire
    mc.relacionar(mc.buscarCaracteristica("Gestor aire"), mc.buscarCaracteristica("HQC"), "Opcional")

    # 2. HQC *requiere* sus dos sub-características obligatorias
    mc.relacionar(mc.buscarCaracteristica("HQC"), mc.buscarCaracteristica("Backend"), "Obligatoria")
    mc.relacionar(mc.buscarCaracteristica("HQC"), mc.buscarCaracteristica("Algoritmo"), "Obligatoria")

    # 3. Relaciones XOR para elegir UN Backend
    mc.relacionar(mc.buscarCaracteristica("Backend"), mc.buscarCaracteristica("Qiskit Simulator"), "XOR")
    mc.relacionar(mc.buscarCaracteristica("Backend"), mc.buscarCaracteristica("SpinQ Simulator"), "XOR")
    mc.relacionar(mc.buscarCaracteristica("Backend"), mc.buscarCaracteristica("TQL Simulator"), "XOR")

    # 4. Relaciones XOR para elegir UN Algoritmo
    mc.relacionar(mc.buscarCaracteristica("Algoritmo"), mc.buscarCaracteristica("QAOA"), "XOR")
    mc.relacionar(mc.buscarCaracteristica("Algoritmo"), mc.buscarCaracteristica("VQE"), "XOR")

    # 5. Conectar tu nueva funcionalidad clásica
    mc.relacionar(mc.buscarCaracteristica("Turismo"), mc.buscarCaracteristica("Optimizacion de rutas"), "Opcional")

    # 6. Esta es la conexión clave: Clásico -> Cuántico
    mc.relacionar(mc.buscarCaracteristica("Optimizacion de rutas"), mc.buscarCaracteristica("HQC"), "Requiere")
    # --- FIN DE TU MODIFICACIÓN ---
    #print(mc.calcularPosiblesEstados())
    mc.almacenarPosiblesEstados("data/datos.csv", mc.permutarCaracteristicas(mc.calcularPosiblesEstados()))
    #print(mc.permutarCaracteristicas(mc.calcularPosiblesEstados()))
    return mc

if __name__ == "__main__":
    print("Iniciando la generación de 'data/datos.csv'...")
    generarPosiblesEstados()
    print("¡Archivo 'data/datos.csv' generado/actualizado exitosamente!")