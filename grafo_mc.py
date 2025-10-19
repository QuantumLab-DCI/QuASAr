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
            nodoArbol.append([nodo[0] + " activada"])
        if (nodo[1] == "Opcional"):
            nodoArbol.append([nodo[0] + " activada", nodo[0] + " desactivada"])
        if (nodo[1] == "XOR"):
            caracteristicas = self.buscarRelacionesXOR(nodo[0])
            for combo in itertools.product([True, False], repeat=len(caracteristicas)):
                if combo.count(True) != 1:
                    continue
                resultado = []
                for i, activado in enumerate(combo):
                    estado = "activada" if activado else "desactivada"
                    resultado.append(f"{caracteristicas[i]} {estado}")
                #print(resultado)
                nodoArbol.append(resultado)
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

    def removerRelacionesInvalidas(self,reconfiguraciones):
        posiblesEstados= []
        print("reconfiguraciones iniciales",len(reconfiguraciones))
        for nodo in reconfiguraciones:
            relacionInvalida = False
            for caracteristica in nodo:
                nombreCaracteristica = caracteristica.replace(" desactivada", "")
                caracteristicaBuscada = self.buscarCaracteristica(nombreCaracteristica)
                if caracteristicaBuscada != None:
                    for relacion in caracteristicaBuscada.getRelaciones:
                        dato = relacion[0] +" activada"
                        #print(dato)
                        if dato in nodo and relacion[1] != "Requiere":
                            relacionInvalida = True
                else:
                    nombreCaracteristicaActivada = caracteristica.replace(" activada", "")
                    caracteristicaBuscada = self.buscarCaracteristica(nombreCaracteristicaActivada)
                    existeOR = any("OR" in arreglo for arreglo in caracteristicaBuscada.getRelaciones)
                    if existeOR:
                        contadorCaracteristicasActivadas = 0
                        for relacion in caracteristicaBuscada.getRelaciones:
                            if relacion[1] == "OR":
                                dato = relacion[0] + " activada"
                                if dato in nodo:
                                    contadorCaracteristicasActivadas+=1
                        if contadorCaracteristicasActivadas == 0:
                            relacionInvalida = True
            if not relacionInvalida:
                posiblesEstados.append(nodo)
            else:
                print(nodo)
        print("reconfiguraciones finales sin excluir require",len(posiblesEstados))
        return self.filtrarRelacionesRequire(posiblesEstados)



    def filtrarRelacionesRequire(self, reconfiguraciones):
        posiblesEstados = []
        for nodo in reconfiguraciones:
            caracteristicasRequeridas = []
            condicion = True
            for caracteristica in nodo:
                nombreCaracteristica = caracteristica.replace(" activada","")
                caracteristicaBuscada = self.buscarCaracteristica(nombreCaracteristica)
                if caracteristicaBuscada != None:
                    #print(caracteristicaBuscada.nombre)
                    for ramas in caracteristicaBuscada.getRelaciones:
                        #print(ramas[1])
                        if(ramas[1]== "Requiere"):
                            caracteristicasRequeridas.append(ramas[0] + " activada")
                            #print("llego a requerida")
            for requeridas in caracteristicasRequeridas:
                if not requeridas in nodo:
                    condicion = False
                    #print("llego a falso")
            if condicion:
                posiblesEstados.append(nodo)
        print(len(posiblesEstados))
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
        print(posiblesEstados)
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
        print(reconfiguraciones)
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
    #print(mc.calcularPosiblesEstados())
    mc.almacenarPosiblesEstados("data/datos.csv", mc.permutarCaracteristicas(mc.calcularPosiblesEstados()))
    #print(mc.permutarCaracteristicas(mc.calcularPosiblesEstados()))
    return mc



