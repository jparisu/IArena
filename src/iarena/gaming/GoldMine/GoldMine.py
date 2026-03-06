"""GoldMine public facade with classes and shared type aliases."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

from iarena.utilizing.square_map.SquareMap import Coordinate, Direction, SquareMap

if TYPE_CHECKING:
    from iarena.gaming.GoldMine.GoldMineGameConfiguration import GoldMineGameConfiguration
    from iarena.gaming.GoldMine.GoldMineGameGenerator import GoldMineGameGenerator
    from iarena.gaming.GoldMine.GoldMineGameRules import GoldMineGameRules
    from iarena.gaming.GoldMine.GoldMineHintMode import GoldMineHintMode
    from iarena.gaming.GoldMine.GoldMineMovement import GoldMineMovement
    from iarena.gaming.GoldMine.GoldMineOrchestrator import GoldMineOrchestrator
    from iarena.gaming.GoldMine.GoldMinePlayer import GoldMinePlayer
    from iarena.gaming.GoldMine.GoldMinePosition import GoldMinePosition

CostType = float
GoldMineCoordinate = Coordinate
GoldMineDirection = Direction
GoldMineSquareMap = SquareMap[float]

_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    "GoldMineGameConfiguration": ("iarena.gaming.GoldMine.GoldMineGameConfiguration", "GoldMineGameConfiguration"),
    "GoldMineGameGenerator": ("iarena.gaming.GoldMine.GoldMineGameGenerator", "GoldMineGameGenerator"),
    "GoldMineGameRules": ("iarena.gaming.GoldMine.GoldMineGameRules", "GoldMineGameRules"),
    "GoldMineHintMode": ("iarena.gaming.GoldMine.GoldMineHintMode", "GoldMineHintMode"),
    "GoldMineMovement": ("iarena.gaming.GoldMine.GoldMineMovement", "GoldMineMovement"),
    "GoldMineOrchestrator": ("iarena.gaming.GoldMine.GoldMineOrchestrator", "GoldMineOrchestrator"),
    "GoldMinePlayer": ("iarena.gaming.GoldMine.GoldMinePlayer", "GoldMinePlayer"),
    "GoldMinePosition": ("iarena.gaming.GoldMine.GoldMinePosition", "GoldMinePosition"),
}


def __getattr__(name: str) -> Any:
    """Lazily resolve class exports to avoid circular imports.

    Args:
        name: Requested module attribute.

    Returns:
        Resolved attribute value.
    """
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, symbol_name = _LAZY_EXPORTS[name]
    module = import_module(module_name)
    return getattr(module, symbol_name)


def __dir__() -> list[str]:
    """Return directory listing including lazy exports.

    Args:
        None.

    Returns:
        Sorted list of visible module attributes.
    """
    return sorted(set(globals()) | set(_LAZY_EXPORTS))


__all__ = [
    "CostType",
    "GoldMineGameConfiguration",
    "GoldMineGameGenerator",
    "GoldMineGameRules",
    "GoldMineCoordinate",
    "GoldMineDirection",
    "GoldMineHintMode",
    "GoldMineMovement",
    "GoldMineOrchestrator",
    "GoldMinePlayer",
    "GoldMinePosition",
    "GoldMineSquareMap",
]
