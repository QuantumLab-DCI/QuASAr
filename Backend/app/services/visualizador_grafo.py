from graphviz import Digraph
# --- INICIO DE MODIFICACIÓN DE IMPORTS ---
# Apuntamos a los módulos que ahora están en 'app/core'
from app.core import grafo_mc
from app.core import punto_variacion
import os  # <--- NUEVO: Necesario para verificar si existe evidencia física
# --- FIN DE MODIFICACIÓN DE IMPORTS ---

# ====== Ajustes visuales reutilizables ======
FONT_NAME = "Arial"
EDGE_COLOR = "#4d4d4d"
FEATURE_FILL = "#eef3ff"   # azul muy claro para el modelo
FEATURE_BORDER = "#7aa6ff"

ACTIVE_GREEN = "#33a02c"
INACTIVE_RED = "#e31a1c"
EVIDENCE_PURPLE = "#984ea3" # <--- NUEVO: Color para nodos con evidencia cuántica
STATE_TEXT = "white"

def _wrap_label(text: str, width: int = 18) -> str:
    """
    Envuelve etiquetas largas para que no desborden los nodos.
    """
    if not text:
        return ""
    words = str(text).split()
    lines, line = [], []
    count = 0
    for w in words:
        wlen = len(w)
        if count + (1 if line else 0) + wlen <= width:
            line.append(w)
            count = count + (1 if line[:-1] else 0) + wlen
        else:
            lines.append(" ".join(line))
            line = [w]
            count = wlen
    if line:
        lines.append(" ".join(line))
    return "\n".join(lines)


def _base_graph(comment: str) -> Digraph:
    """
    Crea un grafo con atributos visuales mejorados.
    """
    dot = Digraph(comment=comment)
    # Layout horizontal, más espacio entre nodos, líneas suaves
    dot.attr(
        rankdir="LR", splines="spline", overlap="false",
        nodesep="0.4", ranksep="0.6", pad="0.1",
        fontname=FONT_NAME, fontsize="11", dpi="110"
    )
    dot.attr("node",
             fontname=FONT_NAME, fontsize="10",
             shape="box", style="rounded,filled",
             color=FEATURE_BORDER, penwidth="1.2",
             fillcolor=FEATURE_FILL)
    dot.attr("edge",
             color=EDGE_COLOR, arrowsize="0.8", penwidth="1.2")
    return dot


def _legend(dot: Digraph, es_estado: bool = False) -> None:
    """
    Leyenda compacta para entender colores.
    """
    with dot.subgraph(name="cluster_legend") as c:
        c.attr(label="Leyenda", style="rounded", color="#d9d9d9",
               fontname=FONT_NAME, fontsize="10")
        if es_estado:
            c.node("L_ACT", "Activo", shape="box",
                   style="rounded,filled", fillcolor=ACTIVE_GREEN,
                   fontcolor=STATE_TEXT, color=ACTIVE_GREEN)
            c.node("L_INA", "Inactivo", shape="box",
                   style="rounded,filled", fillcolor=INACTIVE_RED,
                   fontcolor=STATE_TEXT, color=INACTIVE_RED)
            # --- NUEVO ITEM DE LEYENDA ---
            c.node("L_EVI", "Con Evidencia Cuántica", shape="box",
                   style="rounded,filled", fillcolor=EVIDENCE_PURPLE,
                   fontcolor=STATE_TEXT, color=EVIDENCE_PURPLE)
            c.edge("L_ACT", "L_INA", style="invis")  # mantener compacto
            c.edge("L_INA", "L_EVI", style="invis")
        else:
            c.node("L_F", "Característica", shape="box",
                   style="rounded,filled", fillcolor=FEATURE_FILL,
                   color=FEATURE_BORDER)
            c.node("L_R", "Requiere (dependencia)", shape="diamond",
                   style="filled", fillcolor="#f1e4ff", color="#a47bdc",
                   fontname=FONT_NAME)
            c.edge("L_F", "L_R", style="invis")


def generar_visualizacion_modelo(mc, nombre_archivo='modelo_caracteristicas'):
    """
    Genera una visualización estática del Modelo de Características completo.
    - Layout horizontal (LR)
    - Etiquetas envueltas
    - Leyenda
    - Exporta SVG y PNG
    """
    dot = _base_graph(comment="Modelo de Características")

    # Añadir todas las características como nodos
    for caracteristica in mc.caracteristicas:
        nombre = caracteristica.getNombre
        dot.node(nombre, _wrap_label(nombre))

    # Añadir las relaciones como flechas
    for caracteristica in mc.caracteristicas:
        nombre_padre = caracteristica.getNombre
        for relacion in caracteristica.getRelaciones:
            nombre_hijo, tipo_relacion = relacion[0], relacion[1]
            if tipo_relacion == "Requiere":
                # Dependencia punteada y color morado suave
                dot.edge(
                    nombre_padre, nombre_hijo,
                    style="dashed", arrowhead="normal",
                    label="Requiere", fontsize="9",
                    color="#6a3d9a", fontname=FONT_NAME,
                    constraint="false"
                )
            else:
                # Jerárquica normal
                dot.edge(
                    nombre_padre, nombre_hijo,
                    label=_wrap_label(tipo_relacion, 14),
                    fontsize="9", fontname=FONT_NAME
                )

    _legend(dot, es_estado=False)

    # Exportar SVG y PNG
    dot.format = "svg"
    dot.render(nombre_archivo, view=False, cleanup=True)
    dot.format = "png"
    dot.render(nombre_archivo, view=False, cleanup=True)
    print(f"✅ Visualización del modelo guardada como {nombre_archivo}.svg y .png")


def generar_visualizacion_estado(punto_variacion, mc, nombre_archivo='estado_actual'):
    """
    Genera una visualización del estado actual del sistema:
    - Nodos ACTIVOS en VERDE, INACTIVOS en ROJO (texto blanco)
    - Si hay evidencia cuántica real (archivos generados), el nodo HQC se pinta PÚRPURA.
    - Activos con borde más grueso
    - Layout horizontal, etiquetas envueltas, leyenda
    - Exporta SVG y PNG
    """
    dot = _base_graph(comment="Estado Actual del Sistema")

    # Actualizamos esquema de colores por estado (sobrescribe defaults)
    # Nota: para el estado, definimos nodos individualmente
    # Obtener configuración actual desde el punto de variación
    configuracion = {}
    try:
        configuracion = punto_variacion.obtenerConfiguracion()
    except Exception:
        configuracion = {}

    # Nombres de todas las características
    nombres_caracteristicas = [c.getNombre for c in mc.caracteristicas]

    # Normalizamos diccionario de estado: por defecto, inactivo
    nodos_agregados = {n: False for n in nombres_caracteristicas}

    # Mapear llaves del dict de config (que suelen venir normalizadas)
    for nombre, estado in configuracion.items():
        nombre_formal = next(
            (n for n in nombres_caracteristicas
             if n.replace(" ", "_").lower() == str(nombre).lower()),
            None
        )
        if nombre_formal is not None:
            nodos_agregados[nombre_formal] = bool(estado)

    # --- INICIO DE MODIFICACIÓN: DETECCIÓN DE EVIDENCIA ---
    # Verificamos si existen los archivos de evidencia generados por los adaptadores.
    # La ruta es relativa a este archivo: app/services/visualizador_grafo.py -> ../../data
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
    tiene_evidencia = False
    if os.path.exists(os.path.join(base_path, "qiskit_circuit_evidence.png")) or \
       os.path.exists(os.path.join(base_path, "cirq_convergence_evidence.png")):
        tiene_evidencia = True
    # --- FIN DE MODIFICACIÓN ---

    # Dibujar nodos según estado
    for nombre, activo in nodos_agregados.items():
        color_fill = INACTIVE_RED
        color_font = STATE_TEXT
        pen_width = "1.2"
        
        if activo:
            color_fill = ACTIVE_GREEN
            pen_width = "2.2"
            
            # --- INICIO DE MODIFICACIÓN: COLOR PÚRPURA PARA HQC ---
            # Si hay evidencia física y el nodo es relevante (HQC o Simuladores), usar púrpura
            if tiene_evidencia and (nombre == "HQC" or "Simulator" in nombre):
                color_fill = EVIDENCE_PURPLE
            # --- FIN DE MODIFICACIÓN ---

        dot.node(
            nombre, _wrap_label(nombre),
            fillcolor=color_fill, fontcolor=color_font,
            color=color_fill, penwidth=pen_width
        )

    # Añadir relaciones (igual que en el modelo) para mantener coherencia
    for caracteristica in mc.caracteristicas:
        nombre_padre = caracteristica.getNombre
        for relacion in caracteristica.getRelaciones:
            nombre_hijo, tipo_relacion = relacion[0], relacion[1]
            if tipo_relacion == "Requiere":
                dot.edge(
                    nombre_padre, nombre_hijo,
                    style="dashed", arrowhead="normal",
                    label="Requiere", fontsize="9",
                    color="#6a3d9a", fontname=FONT_NAME,
                    constraint="false"
                )
            else:
                dot.edge(
                    nombre_padre, nombre_hijo,
                    label=_wrap_label(tipo_relacion, 14),
                    fontsize="9", fontname=FONT_NAME
                )

    _legend(dot, es_estado=True)

    # Exportar SVG y PNG
    dot.format = "svg"
    dot.render(nombre_archivo, view=False, cleanup=True)
    dot.format = "png"
    dot.render(nombre_archivo, view=False, cleanup=True)
    print(f"🔄 Visualización de estado guardada como {nombre_archivo}.svg y .png")