"""Hanoi public facade with classes and shared type aliases."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from iarena.gaming.Hanoi.HanoiGameConfiguration import HanoiGameConfiguration
    from iarena.gaming.Hanoi.HanoiGameGenerator import HanoiGameGenerator
    from iarena.gaming.Hanoi.HanoiGameRules import HanoiGameRules
    from iarena.gaming.Hanoi.HanoiMovement import HanoiMovement
    from iarena.gaming.Hanoi.HanoiOrchestrator import HanoiOrchestrator
    from iarena.gaming.Hanoi.HanoiPlayer import HanoiPlayer
    from iarena.gaming.Hanoi.HanoiPosition import HanoiPosition

HanoiDisc = int
HanoiPegIndex = int
HanoiPegState = tuple[HanoiDisc, ...]
HanoiPegsState = tuple[HanoiPegState, ...]

_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    "HanoiGameConfiguration": ("iarena.gaming.Hanoi.HanoiGameConfiguration", "HanoiGameConfiguration"),
    "HanoiGameGenerator": ("iarena.gaming.Hanoi.HanoiGameGenerator", "HanoiGameGenerator"),
    "HanoiGameRules": ("iarena.gaming.Hanoi.HanoiGameRules", "HanoiGameRules"),
    "HanoiMovement": ("iarena.gaming.Hanoi.HanoiMovement", "HanoiMovement"),
    "HanoiOrchestrator": ("iarena.gaming.Hanoi.HanoiOrchestrator", "HanoiOrchestrator"),
    "HanoiPlayer": ("iarena.gaming.Hanoi.HanoiPlayer", "HanoiPlayer"),
    "HanoiPosition": ("iarena.gaming.Hanoi.HanoiPosition", "HanoiPosition"),
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
    "HanoiDisc",
    "HanoiGameConfiguration",
    "HanoiGameGenerator",
    "HanoiGameRules",
    "HanoiMovement",
    "HanoiOrchestrator",
    "HanoiPegIndex",
    "HanoiPegState",
    "HanoiPegsState",
    "HanoiPlayer",
    "HanoiPosition",
]
