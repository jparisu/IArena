"""Typed configuration model for Hanoi game generation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from iarena.desining.gaming.GameConfiguration import GameConfiguration
from iarena.gaming.Hanoi.Hanoi import HanoiPegIndex


@dataclass(frozen=True, slots=True)
class HanoiGameConfiguration:
    """Store all typed values required to construct Hanoi rules."""

    n_disks: int
    start_peg: HanoiPegIndex = 0
    target_peg: HanoiPegIndex = 2
    n_pegs: int = 3

    @staticmethod
    def _require(values: Mapping[str, Any], key: str) -> Any:
        """Read one required key from a mapping.

        Args:
            values: Source mapping.
            key: Required key.

        Returns:
            Value associated with ``key``.

        Raises:
            ValueError: If the key does not exist.
        """
        if key not in values:
            raise ValueError(f"missing required key '{key}'")
        return values[key]

    @staticmethod
    def _parse_int(raw: Any, key: str) -> int:
        """Parse one integer field.

        Args:
            raw: Raw field value.
            key: Field name used in error messages.

        Returns:
            Parsed integer.

        Raises:
            TypeError: If ``raw`` cannot be parsed as integer.
        """
        if isinstance(raw, bool):
            raise TypeError(f"{key} must be an integer")
        if isinstance(raw, (int, float, str)):
            try:
                return int(raw)
            except ValueError as exc:
                raise TypeError(f"{key} must be an integer") from exc
        raise TypeError(f"{key} must be an integer")

    @classmethod
    def from_dict(cls, values: Mapping[str, Any]) -> HanoiGameConfiguration:
        """Build Hanoi configuration from a dictionary-like payload.

        Args:
            values: Raw configuration mapping.

        Returns:
            Parsed ``HanoiGameConfiguration``.
        """
        return cls(
            n_disks=cls._parse_int(cls._require(values, "n_disks"), "n_disks"),
            start_peg=cls._parse_int(values.get("start_peg", 0), "start_peg"),
            target_peg=cls._parse_int(values.get("target_peg", 2), "target_peg"),
            n_pegs=cls._parse_int(values.get("n_pegs", 3), "n_pegs"),
        )

    @classmethod
    def from_game_configuration(cls, configuration: GameConfiguration) -> HanoiGameConfiguration:
        """Build Hanoi configuration from generic game configuration.

        Args:
            configuration: Generic configuration object.

        Returns:
            Parsed ``HanoiGameConfiguration``.
        """
        return cls.from_dict(configuration.to_dict())

    @classmethod
    def from_yaml(cls, yaml_content: str) -> HanoiGameConfiguration:
        """Build Hanoi configuration from YAML text.

        Args:
            yaml_content: YAML content string.

        Returns:
            Parsed ``HanoiGameConfiguration``.
        """
        configuration = GameConfiguration.from_yaml(yaml_content)
        return cls.from_game_configuration(configuration)

    @classmethod
    def from_yaml_file(cls, file_path: str | Path) -> HanoiGameConfiguration:
        """Build Hanoi configuration from a YAML file.

        Args:
            file_path: Path to the YAML configuration file.

        Returns:
            Parsed ``HanoiGameConfiguration``.
        """
        configuration = GameConfiguration.from_yaml_file(file_path)
        return cls.from_game_configuration(configuration)

    def to_dict(self) -> dict[str, Any]:
        """Serialize this configuration into a plain dictionary.

        Args:
            None.

        Returns:
            Dictionary with serializable configuration values.
        """
        return {
            "n_disks": self.n_disks,
            "start_peg": self.start_peg,
            "target_peg": self.target_peg,
            "n_pegs": self.n_pegs,
        }
