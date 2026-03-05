"""Utility helpers for IArena runtime support."""

from iarena.utilizing.protocoling import (
    IPlotRenderable,
    ITextRenderable,
    as_text,
    supports_plotting,
    supports_text_rendering,
)
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator
from iarena.utilizing.Timer import Timer

__all__ = [
    "IPlotRenderable",
    "ITextRenderable",
    "RandomGenerator",
    "Timer",
    "as_text",
    "supports_plotting",
    "supports_text_rendering",
]
