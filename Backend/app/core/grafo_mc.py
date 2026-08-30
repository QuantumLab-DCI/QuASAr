from typing import List, Tuple, Optional, Any

class Nodo:
    """
    Represent a node in the Feature Model graph.
    Each node has a name and a list of relationships with other nodes.
    """
    def __init__(self, nombre: str):
        self._nombre: str = nombre
        self._relaciones: List[List[Any]] = [] # List of [Node, RelationshipType]

    def agregarRelacion(self, nodo_info: List[Any]):
        """
        Add a relationship to this node.
        :param nodo_info: List containing [DestinationNodeName, RelationshipType]
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
    Manage the Feature Model as a graph of nodes.
    Support adding features and defining relationships between them.
    """
    def __init__(self):
        self.caracteristicas: List[Nodo] = []

    def agregarCaracteristica(self, nodo: Nodo):
        self.caracteristicas.append(nodo)

    def relacionar(self, nodo1: Nodo, nodo2: Nodo, tipoRelacion: str):
        """
        Establish a unidirectional relationship from nodo1 to nodo2.
        :param tipoRelacion: "Obligatoria", "Opcional", "XOR", "OR", "Requiere"
        """
        # Store [Node2Name, Type] in Nodo1's relationship list
        nodo1.agregarRelacion([nodo2.getNombre, tipoRelacion])

    def buscarCaracteristica(self, nombreCaracteristica: str) -> Optional[Nodo]:
        """Find a node by name."""
        for rama in self.caracteristicas:
            if rama.getNombre == nombreCaracteristica:
                return rama
        return None
    
    # --- START OF NEW FUNCTION ---
    # ... (remainder of the previous code)

    def exportar_reglas_texto(self) -> str:
        """
        Generate a simple text string that describes the model rules
        for the LLM prompt.
        IMPROVEMENT: Include explicit negative rules to prevent hallucinations.
        """
        reglas = []
        
        # Iterate over the features and their relationships
        for caracteristica in self.caracteristicas:
            nombre_padre = caracteristica.getNombre
            
            # Hierarchy rules (Mandatory, Optional, XOR, OR)
            hijos_xor = []
            hijos_or = []
            
            # --- NEW: List of all children for negative rules ---
            todos_hijos = [] 

            for rel in caracteristica.getRelaciones:
                nombre_hijo, tipo = rel[0], rel[1]
                todos_hijos.append(nombre_hijo) # Store the child

                if tipo == "Obligatoria":
                    reglas.append(f"- Si '{nombre_padre}' está ACTIVO -> '{nombre_hijo}' OBLIGATORIAMENTE ACTIVO.")
                elif tipo == "Opcional":
                    reglas.append(f"- Si '{nombre_padre}' está ACTIVO -> '{nombre_hijo}' es Opcional.")
                elif tipo == "XOR":
                    hijos_xor.append(nombre_hijo)
                elif tipo == "OR":
                    hijos_or.append(nombre_hijo)
            
            # --- CRITICAL IMPROVEMENT: EXPLICIT NEGATIVE RULE ---
            # This prevents the hallucinated activation of children without their parent
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

            # 'Requires' rules
            for rel in caracteristica.getRelaciones:
                if rel[1] == "Requiere":
                    reglas.append(f"- REGLA GLOBAL: '{nombre_padre}' REQUIERE '{rel[0]}'. (No activar '{nombre_padre}' si '{rel[0]}' está inactivo).")

        # Remove duplicates and sort
        reglas_unicas = sorted(list(set(reglas)))
        
        # Find the root
        raiz = self.buscarCaracteristica("Gestor aire")
        if raiz:
            reglas_unicas.insert(0, "El nodo raíz 'Gestor aire' está siempre activo.")

        return "\n".join(reglas_unicas)
    # --- END OF NEW FUNCTION ---

    #
    # --- OBSOLETE FUNCTIONS REMOVED ---
    # (removerRelacionesInvalidas, permutarCaracteristicas, estadoTipoRelacion, etc.)
    #

    def obtenerRelacionesCaracteristicaConRestriccion(self, nombreCaracteristica):
        """
        This function is used by 'punto_variacion.py', so it is retained.
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

        # --- START OF MODIFICATION ---
    mc.agregarCaracteristica(Nodo("HQC")) # Main node
    mc.agregarCaracteristica(Nodo("Backend"))
    mc.agregarCaracteristica(Nodo("Algoritmo"))

    # Backends (3 shown as an example)
    mc.agregarCaracteristica(Nodo("Qiskit Simulator"))
    mc.agregarCaracteristica(Nodo("Cirq Simulator")) # <--- NEW

    # Algorithms (2 shown as an example)
    mc.agregarCaracteristica(Nodo("QAOA"))
    mc.agregarCaracteristica(Nodo("VQE"))

    # New classical functionality that will use HQC
    mc.agregarCaracteristica(Nodo("Optimizacion de rutas"))
    # --- END OF MODIFICATION ---

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
    # --- START OF MODIFICATION ---
    # 1. HQC is optional and depends on Gestor aire
    mc.relacionar(mc.buscarCaracteristica("Gestor aire"), mc.buscarCaracteristica("HQC"), "Opcional")

    # 2. HQC *requires* its two mandatory subfeatures
    mc.relacionar(mc.buscarCaracteristica("HQC"), mc.buscarCaracteristica("Backend"), "Obligatoria")
    mc.relacionar(mc.buscarCaracteristica("HQC"), mc.buscarCaracteristica("Algoritmo"), "Obligatoria")

    # 3. XOR relationships for selecting ONE backend
    mc.relacionar(mc.buscarCaracteristica("Backend"), mc.buscarCaracteristica("Qiskit Simulator"), "XOR")
    mc.relacionar(mc.buscarCaracteristica("Backend"), mc.buscarCaracteristica("Cirq Simulator"), "XOR") # <--- NEW

    # 4. XOR relationships for selecting ONE algorithm
    mc.relacionar(mc.buscarCaracteristica("Algoritmo"), mc.buscarCaracteristica("QAOA"), "XOR")
    mc.relacionar(mc.buscarCaracteristica("Algoritmo"), mc.buscarCaracteristica("VQE"), "XOR")

    # 5. Connect the new classical functionality
    mc.relacionar(mc.buscarCaracteristica("Turismo"), mc.buscarCaracteristica("Optimizacion de rutas"), "Opcional")

    # 6. This is the key connection: Classical -> Quantum
    mc.relacionar(mc.buscarCaracteristica("Optimizacion de rutas"), mc.buscarCaracteristica("HQC"), "Requiere")
    # --- END OF MODIFICATION ---
    
    # --- THE CALL THAT STORED THE CSV WAS REMOVED ---
    
    return mc

# --- THE if __name__ == "__main__": BLOCK WAS REMOVED ---
