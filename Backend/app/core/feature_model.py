from typing import Any


MANDATORY = "MANDATORY"
OPTIONAL = "OPTIONAL"
REQUIRES = "REQUIRES"
EXCLUDES = "EXCLUDES"


class FeatureNode:
    """Represent one keyed and labeled feature in a feature model."""

    def __init__(self, key: str, label: str) -> None:
        self.key = key
        self.label = label
        self.relationships: list[list[Any]] = []

    def add_relationship(self, child_key: str, relationship_type: str) -> None:
        self.relationships.append([child_key, relationship_type])


class FeatureModel:
    """Manage the feature model and its hierarchy and cross-tree constraints."""

    def __init__(self) -> None:
        self.features: list[FeatureNode] = []

    def add_feature(self, feature: FeatureNode) -> None:
        self.features.append(feature)

    def add_relationship(
        self,
        parent: FeatureNode,
        child: FeatureNode,
        relationship_type: str,
    ) -> None:
        parent.add_relationship(child.key, relationship_type)

    def find_feature(self, key: str) -> FeatureNode | None:
        return next((feature for feature in self.features if feature.key == key), None)

    def export_rules_text(self) -> str:
        """Render explicit feature-model rules for the LLM prompt."""
        rules: list[str] = []
        for feature in self.features:
            xor_children: list[str] = []
            or_children: list[str] = []
            hierarchical_children: list[str] = []

            for child_key, relationship_type in feature.relationships:
                if relationship_type != REQUIRES and relationship_type != EXCLUDES:
                    hierarchical_children.append(child_key)
                if relationship_type == MANDATORY:
                    rules.append(
                        f"- If '{feature.key}' is enabled, '{child_key}' must be enabled."
                    )
                elif relationship_type == OPTIONAL:
                    rules.append(
                        f"- If '{feature.key}' is enabled, '{child_key}' is optional."
                    )
                elif relationship_type == "XOR":
                    xor_children.append(child_key)
                elif relationship_type == "OR":
                    or_children.append(child_key)
                elif relationship_type == REQUIRES:
                    rules.append(
                        f"- Global constraint: '{feature.key}' requires '{child_key}'."
                    )
                elif relationship_type == EXCLUDES:
                    rules.append(
                        f"- Global constraint: '{feature.key}' excludes '{child_key}'."
                    )

            if hierarchical_children:
                children = ", ".join(f"'{key}'" for key in hierarchical_children)
                rules.append(
                    f"- If '{feature.key}' is disabled, all hierarchical children "
                    f"({children}) must be disabled."
                )
            if xor_children:
                rules.append(
                    f"- If '{feature.key}' is enabled, exactly one of "
                    f"[{', '.join(xor_children)}] must be enabled."
                )
            if or_children:
                rules.append(
                    f"- If '{feature.key}' is enabled, at least one of "
                    f"[{', '.join(or_children)}] must be enabled."
                )

        unique_rules = sorted(set(rules))
        unique_rules.insert(0, "The root feature 'air_quality_manager' is always enabled.")
        return "\n".join(unique_rules)

    def get_hierarchical_children(self, feature_key: str) -> list[str]:
        feature = self.find_feature(feature_key)
        if feature is None:
            return []
        return [
            child_key
            for child_key, relationship_type in feature.relationships
            if relationship_type not in {REQUIRES, EXCLUDES}
        ]


def build_air_quality_feature_model() -> FeatureModel:
    """Build the self-adaptive air-quality system feature model."""
    model = FeatureModel()
    feature_definitions = [
        ("air_quality_manager", "Air Quality Manager"),
        ("air_quality_viewer", "Air Quality Viewer"),
        ("wood_burning_restriction_viewer", "Wood-Burning Restriction Viewer"),
        ("tourism", "Tourism"),
        ("indoor_environments", "Indoor Environments"),
        ("outdoor_environments", "Outdoor Environments"),
        ("sports", "Sports"),
        ("entertainment", "Entertainment"),
        ("family_entertainment", "Family Entertainment"),
        ("adult_entertainment", "Adult Entertainment"),
        ("senior_entertainment", "Senior Entertainment"),
        ("hybrid_quantum_computing", "Hybrid Quantum-Classical Computing"),
        ("quantum_backend", "Quantum Backend"),
        ("quantum_algorithm", "Quantum Algorithm"),
        ("qiskit_simulator", "Qiskit Simulator"),
        ("cirq_simulator", "Cirq Simulator"),
        ("qaoa", "QAOA"),
        ("vqe", "VQE"),
        ("route_optimization", "Route Optimization"),
    ]
    for key, label in feature_definitions:
        model.add_feature(FeatureNode(key, label))

    relationships = [
        ("air_quality_manager", "air_quality_viewer", MANDATORY),
        ("air_quality_manager", "tourism", MANDATORY),
        ("air_quality_manager", "sports", OPTIONAL),
        ("air_quality_manager", "entertainment", OPTIONAL),
        ("air_quality_viewer", "wood_burning_restriction_viewer", OPTIONAL),
        ("tourism", "indoor_environments", "XOR"),
        ("tourism", "outdoor_environments", "XOR"),
        ("outdoor_environments", "sports", REQUIRES),
        ("indoor_environments", "wood_burning_restriction_viewer", REQUIRES),
        ("entertainment", "family_entertainment", "OR"),
        ("entertainment", "adult_entertainment", "OR"),
        ("entertainment", "senior_entertainment", "OR"),
        ("air_quality_manager", "hybrid_quantum_computing", OPTIONAL),
        ("hybrid_quantum_computing", "quantum_backend", MANDATORY),
        ("hybrid_quantum_computing", "quantum_algorithm", MANDATORY),
        ("quantum_backend", "qiskit_simulator", "XOR"),
        ("quantum_backend", "cirq_simulator", "XOR"),
        ("quantum_algorithm", "qaoa", "XOR"),
        ("quantum_algorithm", "vqe", "XOR"),
        ("tourism", "route_optimization", OPTIONAL),
        ("route_optimization", "hybrid_quantum_computing", REQUIRES),
    ]
    for parent_key, child_key, relationship_type in relationships:
        model.add_relationship(
            model.find_feature(parent_key),
            model.find_feature(child_key),
            relationship_type,
        )
    return model
