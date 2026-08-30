from graphviz import Digraph
# --- START OF IMPORT MODIFICATION ---
# Reference the modules that are now in 'app/core'
from app.core import grafo_mc
from app.core import punto_variacion
import os  # <--- NEW: Required to check whether physical evidence exists
# --- END OF IMPORT MODIFICATION ---

# ====== Reusable Visual Settings ======
FONT_NAME = "Arial"
EDGE_COLOR = "#4d4d4d"
FEATURE_FILL = "#eef3ff"   # very light blue for the model
FEATURE_BORDER = "#7aa6ff"

ACTIVE_GREEN = "#33a02c"
INACTIVE_RED = "#e31a1c"
EVIDENCE_PURPLE = "#984ea3" # <--- NEW: Color for nodes with quantum evidence
STATE_TEXT = "white"

def _wrap_label(text: str, width: int = 18) -> str:
    """
    Wrap long labels so they do not overflow the nodes.
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
    Create a graph with enhanced visual attributes.
    """
    dot = Digraph(comment=comment)
    # Horizontal layout, more space between nodes, smooth lines
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
    Provide a compact legend for interpreting colors.
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
            # --- NEW LEGEND ITEM ---
            c.node("L_EVI", "Con Evidencia Cuántica", shape="box",
                   style="rounded,filled", fillcolor=EVIDENCE_PURPLE,
                   fontcolor=STATE_TEXT, color=EVIDENCE_PURPLE)
            c.edge("L_ACT", "L_INA", style="invis")  # Keep it compact
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
    Generate a static visualization of the complete Feature Model.
    - Horizontal layout (LR)
    - Wrapped labels
    - Legend
    - Export to SVG and PNG
    """
    dot = _base_graph(comment="Modelo de Características")

    # Add all features as nodes
    for caracteristica in mc.caracteristicas:
        nombre = caracteristica.getNombre
        dot.node(nombre, _wrap_label(nombre))

    # Add relationships as arrows
    for caracteristica in mc.caracteristicas:
        nombre_padre = caracteristica.getNombre
        for relacion in caracteristica.getRelaciones:
            nombre_hijo, tipo_relacion = relacion[0], relacion[1]
            if tipo_relacion == "Requiere":
                # Dotted dependency with a soft purple color
                dot.edge(
                    nombre_padre, nombre_hijo,
                    style="dashed", arrowhead="normal",
                    label="Requiere", fontsize="9",
                    color="#6a3d9a", fontname=FONT_NAME,
                    constraint="false"
                )
            else:
                # Standard hierarchical relationship
                dot.edge(
                    nombre_padre, nombre_hijo,
                    label=_wrap_label(tipo_relacion, 14),
                    fontsize="9", fontname=FONT_NAME
                )

    _legend(dot, es_estado=False)

    # Export to SVG and PNG
    dot.format = "svg"
    dot.render(nombre_archivo, view=False, cleanup=True)
    dot.format = "png"
    dot.render(nombre_archivo, view=False, cleanup=True)
    print(f"✅ Visualización del modelo guardada como {nombre_archivo}.svg y .png")


def generar_visualizacion_estado(punto_variacion, mc, nombre_archivo='estado_actual'):
    """
    Generate a visualization of the current system state:
    - ACTIVE nodes in GREEN and INACTIVE nodes in RED (white text)
    - If real quantum evidence exists (generated files), render the HQC node in PURPLE.
    - Active nodes have a thicker border
    - Horizontal layout, wrapped labels, and legend
    - Export to SVG and PNG
    """
    dot = _base_graph(comment="Estado Actual del Sistema")

    # Update the state color scheme (overrides defaults)
    # Note: define nodes individually for the state visualization
    # Get the current configuration from the variation point
    configuracion = {}
    try:
        configuracion = punto_variacion.obtenerConfiguracion()
    except Exception:
        configuracion = {}

    # Names of all features
    nombres_caracteristicas = [c.getNombre for c in mc.caracteristicas]

    # Normalize the state dictionary; inactive by default
    nodos_agregados = {n: False for n in nombres_caracteristicas}

    # Map configuration dictionary keys, which are usually normalized
    for nombre, estado in configuracion.items():
        nombre_formal = next(
            (n for n in nombres_caracteristicas
             if n.replace(" ", "_").lower() == str(nombre).lower()),
            None
        )
        if nombre_formal is not None:
            nodos_agregados[nombre_formal] = bool(estado)

    # --- START OF MODIFICATION: EVIDENCE DETECTION ---
    # Check whether evidence files generated by the adapters exist.
    # The path is relative to this file: app/services/visualizador_grafo.py -> ../../data
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
    tiene_evidencia = False
    if os.path.exists(os.path.join(base_path, "qiskit_circuit_evidence.png")) or \
       os.path.exists(os.path.join(base_path, "cirq_convergence_evidence.png")):
        tiene_evidencia = True
    # --- END OF MODIFICATION ---

    # Draw nodes according to their state
    for nombre, activo in nodos_agregados.items():
        color_fill = INACTIVE_RED
        color_font = STATE_TEXT
        pen_width = "1.2"
        
        if activo:
            color_fill = ACTIVE_GREEN
            pen_width = "2.2"
            
            # --- START OF MODIFICATION: PURPLE COLOR FOR HQC ---
            # Use purple when physical evidence exists and the node is relevant (HQC or simulators)
            if tiene_evidencia and (nombre == "HQC" or "Simulator" in nombre):
                color_fill = EVIDENCE_PURPLE
            # --- END OF MODIFICATION ---

        dot.node(
            nombre, _wrap_label(nombre),
            fillcolor=color_fill, fontcolor=color_font,
            color=color_fill, penwidth=pen_width
        )

    # Add relationships, as in the model, to maintain consistency
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

    # Export to SVG and PNG
    dot.format = "svg"
    dot.render(nombre_archivo, view=False, cleanup=True)
    dot.format = "png"
    dot.render(nombre_archivo, view=False, cleanup=True)
    print(f"🔄 Visualización de estado guardada como {nombre_archivo}.svg y .png")
