"""Hint modes available in the GoldMine game."""

from __future__ import annotations

from enum import Enum


class GoldMineHintMode(Enum):
    """Represent the hint strategy exposed to the player."""

    NONE = "none"
    COMPASS = "compass"
    PROXIMITY = "proximity"
    DENSITY = "density"

    @classmethod
    def from_value(cls, value: str | None) -> GoldMineHintMode:
        """Parse a user value into a hint mode.

        Args:
            value: Raw hint mode name, case-insensitive.

        Returns:
            Parsed hint mode. When ``value`` is ``None``, returns ``NONE``.
        """
        if value is None:
            return cls.NONE

        normalized = value.strip().lower()
        for mode in cls:
            if normalized in (mode.name.lower(), mode.value):
                return mode

        available = ", ".join(mode.value for mode in cls)
        raise ValueError(f"unknown hint mode '{value}'. Available values: {available}")
