"""Configuration model used to build game rules from dictionaries or YAML."""

from __future__ import annotations

from collections.abc import ItemsView, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class GameConfiguration:
    """Store a normalized configuration payload for one game instance."""

    values: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, values: Mapping[str, Any]) -> GameConfiguration:
        """Build configuration from a mapping.

        Args:
            values: Raw mapping with configuration fields.

        Returns:
            New configuration instance with a copied dictionary.
        """
        return cls(values=dict(values))

    @classmethod
    def from_yaml(cls, yaml_content: str) -> GameConfiguration:
        """Build configuration from a YAML string.

        Args:
            yaml_content: YAML content with configuration fields.

        Returns:
            New configuration instance parsed from YAML.

        Raises:
            RuntimeError: If PyYAML is not installed.
            TypeError: If parsed YAML is not a mapping.
        """
        try:
            import yaml
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Parsing YAML configurations requires the optional 'PyYAML' dependency."
            ) from exc

        parsed = yaml.safe_load(yaml_content)
        if parsed is None:
            return cls()
        if not isinstance(parsed, Mapping):
            raise TypeError("YAML configuration must decode to a mapping")
        return cls.from_dict(parsed)

    @classmethod
    def from_yaml_file(cls, file_path: str | Path) -> GameConfiguration:
        """Build configuration from a YAML file.

        Args:
            file_path: Path to a YAML file.

        Returns:
            New configuration instance parsed from the file content.
        """
        content = Path(file_path).read_text(encoding="utf-8")
        return cls.from_yaml(content)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary copy of this configuration.

        Args:
            None.

        Returns:
            Copied dictionary with the stored configuration values.
        """
        return dict(self.values)

    def get(self, key: str, default: Any = None) -> Any:
        """Return one configuration value using dictionary semantics.

        Args:
            key: Configuration field name.
            default: Value returned when key is missing.

        Returns:
            Stored value for ``key`` or ``default``.
        """
        return self.values.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """Return one configuration value by key.

        Args:
            key: Configuration field name.

        Returns:
            Stored value associated with ``key``.
        """
        return self.values[key]

    def __contains__(self, key: str) -> bool:
        """Return whether a key exists in this configuration.

        Args:
            key: Configuration field name.

        Returns:
            ``True`` when ``key`` exists.
        """
        return key in self.values

    def items(self) -> ItemsView[str, Any]:
        """Return a dynamic view over configuration items.

        Args:
            None.

        Returns:
            Items view over the internal dictionary.
        """
        return self.values.items()
