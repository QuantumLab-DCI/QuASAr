from graphviz import Digraph
import grafo_mc
import punto_variacion

def generar_visualizacion_modelo(mc, nombre_archivo='modelo_caracteristicas'):
    """
    Genera una visualización estática del Modelo de Características completo.
    """
    dot = Digraph(comment='Modelo de Características')
    dot.attr('node', shape='box', style='rounded')
    dot.attr(rankdir='TB', splines='ortho')

    # Añadir todas las características como nodos
    for caracteristica in mc.caracteristicas:
        dot.node(caracteristica.getNombre, caracteristica.getNombre)

    # Añadir las relaciones como flechas
    for caracteristica in mc.caracteristicas:
        nombre_padre = caracteristica.getNombre
        for relacion in caracteristica.getRelaciones:
            nombre_hijo, tipo_relacion = relacion[0], relacion[1]
            if tipo_relacion == "Requiere":
                # La relación 'Requiere' es una dependencia, la dibujamos punteada
                dot.edge(nombre_padre, nombre_hijo, style='dashed', arrowhead='normal', label=tipo_relacion, constraint='false')
            else:
                # Otras relaciones son jerárquicas
                dot.edge(nombre_padre, nombre_hijo, label=tipo_relacion)

    # Guarda el grafo como una imagen PNG
    dot.render(nombre_archivo, format='png', view=False, cleanup=True)
    print(f"✅ Visualización del modelo guardada en {nombre_archivo}.png")

def generar_visualizacion_estado(punto_variacion, mc, nombre_archivo='estado_actual'):
    """
    Genera una visualización del estado actual del sistema, coloreando los nodos
    según si están activos o inactivos.
    """
    configuracion = punto_variacion.obtenerConfiguracion()
    dot = Digraph(comment='Estado Actual del Sistema')
    dot.attr('node', shape='box', style='rounded,filled')
    dot.attr(rankdir='TB', splines='ortho')

    # Nombres de todas las características para referencia
    nombres_caracteristicas = [c.getNombre for c in mc.caracteristicas]
    
    # Crea un diccionario para saber qué nodos ya fueron agregados
    nodos_agregados = {}
    for n in nombres_caracteristicas:
        # Por defecto, si una característica no está en la configuración, la marcamos como inactiva
        nodos_agregados[n] = False 
    
    for nombre, estado in configuracion.items():
        nombre_formal = next((n for n in nombres_caracteristicas if n.replace(" ", "_").lower() == nombre), nombre)
        if nombre_formal in nombres_caracteristicas:
            nodos_agregados[nombre_formal] = estado

    # Añadir nodos y colorearlos según su estado
    for nombre, estado in nodos_agregados.items():
        if estado: # Característica activada
            dot.node(nombre, nombre, fillcolor='lightgreen')
        else: # Característica desactivada
            dot.node(nombre, nombre, fillcolor='#FFDDDD') # Un rojo claro

    # Añadir las mismas relaciones que en el modelo estático
    for caracteristica in mc.caracteristicas:
        nombre_padre = caracteristica.getNombre
        for relacion in caracteristica.getRelaciones:
            nombre_hijo, tipo_relacion = relacion[0], relacion[1]
            if tipo_relacion == "Requiere":
                dot.edge(nombre_padre, nombre_hijo, style='dashed', constraint='false')
            else:
                dot.edge(nombre_padre, nombre_hijo)

    # Guarda el estado actual como una imagen PNG
    dot.render(nombre_archivo, format='png', view=False, cleanup=True)
    print(f"🔄 Visualización de estado actualizada y guardada en {nombre_archivo}.png")