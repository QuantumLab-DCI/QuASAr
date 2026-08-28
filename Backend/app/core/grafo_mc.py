from typing import List, Tuple, Optional, Any

class Nodo:
    """
    Representa un nodo en el Modelo de Características (Grafo).
    Cada nodo tiene un nombre y una lista de relaciones con otros nodos.
    """
    def __init__(self, nombre: str):
        self._nombre: str = nombre
        self._relaciones: List[List[Any]] = [] # Lista de [Nodo, TipoRelacion]

    def agregarRelacion(self, nodo_info: List[Any]):
        """
        Agrega una relación a este nodo.
        :param nodo_info: Lista con [NombreNodoDestino, TipoRelacion]
        """
        self._relaciones.append(nodo_info)

    @property
    def getNombre(self):
        return self._nombre

    @property
    def getRelaciones(self):
        return self._relaciones

class ModeloCaracteristicas:
    """
    Gestiona el Modelo de Características como un grafo de Nodos.
    Permite agregar características y definir relaciones entre ellas.
    """
    def __init__(self):
        self.caracteristicas: List[Nodo] = []

    def agregarCaracteristica(self, nodo: Nodo):
        self.caracteristicas.append(nodo)

    def relacionar(self, nodo1: Nodo, nodo2: Nodo, tipoRelacion: str):
        """
        Establece una relación unidireccional de nodo1 a nodo2.
        :param tipoRelacion: "Obligatoria", "Opcional", "XOR", "OR", "Requiere"
        """
        # Guardamos [NombreNodo2, Tipo] en la lista de relaciones de Nodo1
        nodo1.agregarRelacion([nodo2.getNombre, tipoRelacion])

    def buscarCaracteristica(self, nombreCaracteristica: str) -> Optional[Nodo]:
        """Busca un nodo por su nombre."""
        for rama in self.caracteristicas:
            if rama.getNombre == nombreCaracteristica:
                return rama
        return None
    
    # --- INICIO DE NUEVA FUNCIÓN ---
    # ... (resto del código anterior)

    def exportar_reglas_texto(self) -> str:
        """
        Genera un string de texto simple que describe las reglas
        del modelo para el prompt del LLM.
        MEJORA: Incluye reglas negativas explícitas para evitar alucinaciones.
        """
        reglas = []
        
        # Iterar sobre las características y sus relaciones
        for caracteristica in self.caracteristicas:
            nombre_padre = caracteristica.getNombre
            
            # Reglas de Jerarquía (Obligatoria, Opcional, XOR, OR)
            hijos_xor = []
            hijos_or = []
            
            # --- NUEVO: Lista de todos los hijos para reglas negativas ---
            todos_hijos = [] 

            for rel in caracteristica.getRelaciones:
                nombre_hijo, tipo = rel[0], rel[1]
                todos_hijos.append(nombre_hijo) # Guardamos el hijo

                if tipo == "Obligatoria":
                    reglas.append(f"- Si '{nombre_padre}' está ACTIVO -> '{nombre_hijo}' OBLIGATORIAMENTE ACTIVO.")
                elif tipo == "Opcional":
                    reglas.append(f"- Si '{nombre_padre}' está ACTIVO -> '{nombre_hijo}' es Opcional.")
                elif tipo == "XOR":
                    hijos_xor.append(nombre_hijo)
                elif tipo == "OR":
                    hijos_or.append(nombre_hijo)
            
            # --- MEJORA CRÍTICA: REGLA NEGATIVA EXPLÍCITA ---
            # Esto soluciona la alucinación de activar hijos sin padre
            if todos_hijos:
                lista_hijos_str = ", ".join([f"'{h}'" for h in todos_hijos])
                reglas.append(f"- CRÍTICO: Si '{nombre_padre}' está INACTIVO (False) -> TODOS sus hijos ({lista_hijos_str}) DEBEN estar INACTIVOS.")
            # ------------------------------------------------

            if hijos_xor:
                hijos_str = ", ".join(hijos_xor)
                reglas.append(f"- Si '{nombre_padre}' está ACTIVO -> EXACTAMENTE UNO de [{hijos_str}] debe estar activo.")
            if hijos_or:
                hijos_str = ", ".join(hijos_or)
                reglas.append(f"- Si '{nombre_padre}' está ACTIVO -> AL MENOS UNO de [{hijos_str}] debe estar activo.")

            # Reglas 'Requiere'
            for rel in caracteristica.getRelaciones:
                if rel[1] == "Requiere":
                    reglas.append(f"- REGLA GLOBAL: '{nombre_padre}' REQUIERE '{rel[0]}'. (No activar '{nombre_padre}' si '{rel[0]}' está inactivo).")

        # Limpiar duplicados y ordenar
        reglas_unicas = sorted(list(set(reglas)))
        
        # Encontrar la raíz
        raiz = self.buscarCaracteristica("Gestor aire")
        if raiz:
            reglas_unicas.insert(0, "El nodo raíz 'Gestor aire' está siempre activo.")

        return "\n".join(reglas_unicas)
    # --- FIN DE NUEVA FUNCIÓN ---

    #
    # --- FUNCIONES OBSOLETAS ELIMINADAS ---
    # (removerRelacionesInvalidas, permutarCaracteristicas, estadoTipoRelacion, etc.)
    #

    def obtenerRelacionesCaracteristicaConRestriccion(self, nombreCaracteristica):
        """
        Esta función la usa 'punto_variacion.py', así que la conservamos.
        """
        caracteristica = self.buscarCaracteristica(nombreCaracteristica)
        subCaracteristicas = []
        if caracteristica != None:
            for subCaracteristica in caracteristica.getRelaciones:
                if subCaracteristica[1] != "Requiere" and subCaracteristica[1] != "Excluye":
                    subCaracteristicas.append(subCaracteristica[0])
        return subCaracteristicas

def generarPosiblesEstados():
    mc = ModeloCaracteristicas()
    mc.agregarCaracteristica(Nodo("Gestor aire"))
    mc.agregarCaracteristica(Nodo("Visualizador calidad aire"))
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
    mc.agregarCaracteristica(Nodo("Cirq Simulator")) # <--- NUEVO

    # Algoritmos (ejemplo con 2)
    mc.agregarCaracteristica(Nodo("QAOA"))
    mc.agregarCaracteristica(Nodo("VQE"))

    # Tu nueva funcionalidad clásica que usará el HQC
    mc.agregarCaracteristica(Nodo("Optimizacion de rutas"))
    # --- FIN DE TU MODIFICACIÓN ---

    mc.relacionar(mc.buscarCaracteristica("Gestor aire"),mc.buscarCaracteristica("Visualizador calidad aire"), "Obligatoria")
    mc.relacionar(mc.buscarCaracteristica("Gestor aire"), mc.buscarCaracteristica("Turismo"), "Obligatoria")
    mc.relacionar(mc.buscarCaracteristica("Gestor aire"), mc.buscarCaracteristica("Deportes"), "Opcional")
    mc.relacionar(mc.buscarCaracteristica("Gestor aire"), mc.buscarCaracteristica("Entretenimiento"), "Opcional")
    mc.relacionar(mc.buscarCaracteristica("Visualizador calidad aire"), mc.buscarCaracteristica("Visualizador restriccion uso lena"), "Opcional")
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
    mc.relacionar(mc.buscarCaracteristica("Backend"), mc.buscarCaracteristica("Cirq Simulator"), "XOR") # <--- NUEVO

    # 4. Relaciones XOR para elegir UN Algoritmo
    mc.relacionar(mc.buscarCaracteristica("Algoritmo"), mc.buscarCaracteristica("QAOA"), "XOR")
    mc.relacionar(mc.buscarCaracteristica("Algoritmo"), mc.buscarCaracteristica("VQE"), "XOR")

    # 5. Conectar tu nueva funcionalidad clásica
    mc.relacionar(mc.buscarCaracteristica("Turismo"), mc.buscarCaracteristica("Optimizacion de rutas"), "Opcional")

    # 6. Esta es la conexión clave: Clásico -> Cuántico
    mc.relacionar(mc.buscarCaracteristica("Optimizacion de rutas"), mc.buscarCaracteristica("HQC"), "Requiere")
    # --- FIN DE TU MODIFICACIÓN ---
    
    # --- SE ELIMINÓ LA LLAMADA A ALMACENAR CSV ---
    
    return mc

# --- SE ELIMINÓ EL BLOQUE if __name__ == "__main__": ---