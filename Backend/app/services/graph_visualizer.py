import os

from graphviz import Digraph

from app.core.feature_model import REQUIRES


FONT_NAME = "Arial"
EDGE_COLOR = "#4d4d4d"
FEATURE_FILL = "#eef3ff"
FEATURE_BORDER = "#7aa6ff"
ACTIVE_GREEN = "#33a02c"
INACTIVE_RED = "#e31a1c"
ARTIFACT_PURPLE = "#984ea3"
STATE_TEXT = "white"


def _wrap_label(text: str, width: int = 18) -> str:
    """Wrap a graph label at word boundaries."""
    if not text:
        return ""
    lines: list[str] = []
    line: list[str] = []
    character_count = 0
    for word in str(text).split():
        separator_length = 1 if line else 0
        if character_count + separator_length + len(word) <= width:
            line.append(word)
            character_count += separator_length + len(word)
        else:
            lines.append(" ".join(line))
            line = [word]
            character_count = len(word)
    if line:
        lines.append(" ".join(line))
    return "\n".join(lines)


def _base_graph(comment: str) -> Digraph:
    dot = Digraph(comment=comment)
    dot.attr(
        rankdir="LR",
        splines="spline",
        overlap="false",
        nodesep="0.4",
        ranksep="0.6",
        pad="0.1",
        fontname=FONT_NAME,
        fontsize="11",
        dpi="110",
    )
    dot.attr(
        "node",
        fontname=FONT_NAME,
        fontsize="10",
        shape="box",
        style="rounded,filled",
        color=FEATURE_BORDER,
        penwidth="1.2",
        fillcolor=FEATURE_FILL,
    )
    dot.attr("edge", color=EDGE_COLOR, arrowsize="0.8", penwidth="1.2")
    return dot


def _add_legend(dot: Digraph, is_state_graph: bool = False) -> None:
    with dot.subgraph(name="cluster_legend") as legend:
        legend.attr(
            label="Legend",
            style="rounded",
            color="#d9d9d9",
            fontname=FONT_NAME,
            fontsize="10",
        )
        if is_state_graph:
            legend.node(
                "L_ACTIVE",
                "Enabled",
                style="rounded,filled",
                fillcolor=ACTIVE_GREEN,
                fontcolor=STATE_TEXT,
                color=ACTIVE_GREEN,
            )
            legend.node(
                "L_INACTIVE",
                "Disabled",
                style="rounded,filled",
                fillcolor=INACTIVE_RED,
                fontcolor=STATE_TEXT,
                color=INACTIVE_RED,
            )
            legend.node(
                "L_EVIDENCE",
                "Quantum Artifact Available",
                style="rounded,filled",
                fillcolor=ARTIFACT_PURPLE,
                fontcolor=STATE_TEXT,
                color=ARTIFACT_PURPLE,
            )
            legend.edge("L_ACTIVE", "L_INACTIVE", style="invis")
            legend.edge("L_INACTIVE", "L_EVIDENCE", style="invis")
        else:
            legend.node("L_FEATURE", "Feature", fillcolor=FEATURE_FILL, color=FEATURE_BORDER)
            legend.node(
                "L_REQUIRES",
                "Requires",
                shape="diamond",
                fillcolor="#f1e4ff",
                color="#a47bdc",
            )
            legend.edge("L_FEATURE", "L_REQUIRES", style="invis")


def _add_relationships(dot: Digraph, feature_model) -> None:
    for feature in feature_model.features:
        for child_key, relationship_type in feature.relationships:
            if relationship_type == REQUIRES:
                dot.edge(
                    feature.key,
                    child_key,
                    style="dashed",
                    arrowhead="normal",
                    label="REQUIRES",
                    fontsize="9",
                    color="#6a3d9a",
                    fontname=FONT_NAME,
                    constraint="false",
                )
            else:
                dot.edge(
                    feature.key,
                    child_key,
                    label=_wrap_label(relationship_type, 14),
                    fontsize="9",
                    fontname=FONT_NAME,
                )


def generate_feature_model_visualization(
    feature_model,
    filename: str = "feature_model",
) -> None:
    """Export the complete feature model as SVG and PNG."""
    dot = _base_graph(comment="Feature Model")
    for feature in feature_model.features:
        dot.node(feature.key, _wrap_label(feature.label))
    _add_relationships(dot, feature_model)
    _add_legend(dot)
    for output_format in ("svg", "png"):
        dot.format = output_format
        dot.render(filename, view=False, cleanup=True)
    print(f"Feature-model visualization saved as {filename}.svg and {filename}.png.")


def generate_state_visualization(
    variation_point,
    feature_model,
    filename: str = "current_state",
) -> None:
    """Export the current runtime configuration as SVG and PNG."""
    dot = _base_graph(comment="Current Self-Adaptive System State")
    try:
        configuration = variation_point.get_configuration()
    except Exception:
        configuration = {}

    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
    has_quantum_artifact = any(
        os.path.exists(os.path.join(data_path, artifact_name))
        for artifact_name in (
            "qiskit_circuit_artifact.png",
            "cirq_circuit_artifact.png",
            "cirq_convergence_artifact.png",
        )
    )
    quantum_feature_keys = {
        "hybrid_quantum_computing",
        "qiskit_simulator",
        "cirq_simulator",
    }
    for feature in feature_model.features:
        is_enabled = bool(configuration.get(feature.key, False))
        fill_color = ACTIVE_GREEN if is_enabled else INACTIVE_RED
        pen_width = "2.2" if is_enabled else "1.2"
        if is_enabled and has_quantum_artifact and feature.key in quantum_feature_keys:
            fill_color = ARTIFACT_PURPLE
        dot.node(
            feature.key,
            _wrap_label(feature.label),
            fillcolor=fill_color,
            fontcolor=STATE_TEXT,
            color=fill_color,
            penwidth=pen_width,
        )

    _add_relationships(dot, feature_model)
    _add_legend(dot, is_state_graph=True)
    for output_format in ("svg", "png"):
        dot.format = output_format
        dot.render(filename, view=False, cleanup=True)
    print(f"Current-state visualization saved as {filename}.svg and {filename}.png.")
