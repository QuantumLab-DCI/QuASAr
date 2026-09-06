class ConfiguredFeature:
    """Represent the runtime state and links of one configured feature."""

    def __init__(
        self,
        feature_key: str,
        is_enabled: bool,
        docker_container: str,
        href: str,
    ) -> None:
        self.feature_key = feature_key
        self.is_enabled = is_enabled
        self.docker_container = docker_container
        self.children: list[ConfiguredFeature] = []
        self.href = href

    def add_child(self, feature: "ConfiguredFeature") -> None:
        self.children.append(feature)


class VariationPoint:
    """Manage the selected runtime configuration for the feature model."""

    def __init__(
        self,
        configuration_state: list[str],
        feature_model,
        root_feature_key: str,
    ) -> None:
        configured_features = self._build_configured_features(configuration_state)
        configured_features.append(self._build_root_feature(root_feature_key))
        self._configured_features = self._connect_features(
            configured_features,
            feature_model,
        )
        self._feature_model = feature_model

    def get_configuration(self) -> dict[str, bool]:
        return {
            feature.feature_key: feature.is_enabled
            for feature in self._configured_features
        }

    def get_level_configuration(self, feature_key: str) -> dict | None:
        """Return enabled child links, or None for an unknown feature."""
        for feature in self._configured_features:
            if feature.feature_key == feature_key:
                return {
                    "links": [
                        {"name": child.feature_key, "href": child.href}
                        for child in feature.children
                        if child.is_enabled
                    ]
                }
        return None

    def get_feature_state(self, feature_key: str) -> dict[str, str]:
        """Return link metadata for an enabled feature."""
        for feature in self._configured_features:
            if feature.feature_key == feature_key and feature.is_enabled:
                return {"name": feature.feature_key, "href": feature.href}
        return {}

    def _build_configured_features(
        self,
        configuration_state: list[str],
    ) -> list[ConfiguredFeature]:
        configured_features = []
        for proposition in configuration_state:
            feature_key, state = proposition.rsplit(" ", 1)
            configured_features.append(
                ConfiguredFeature(
                    feature_key=feature_key,
                    is_enabled=state == "enabled",
                    docker_container=feature_key,
                    href=f"/{feature_key}",
                )
            )
        return configured_features

    def _build_root_feature(self, root_feature_key: str) -> ConfiguredFeature:
        return ConfiguredFeature(
            feature_key=root_feature_key,
            is_enabled=True,
            docker_container=root_feature_key,
            href=f"/{root_feature_key}",
        )

    def _connect_features(self, configured_features: list[ConfiguredFeature], feature_model):
        configured_by_key = {
            feature.feature_key: feature for feature in configured_features
        }
        for feature in configured_features:
            for child_key in feature_model.get_hierarchical_children(feature.feature_key):
                child = configured_by_key.get(child_key)
                if child is not None:
                    feature.add_child(child)
        return configured_features
