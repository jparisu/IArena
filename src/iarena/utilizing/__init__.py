"""Utility helpers for IArena runtime support."""

from iarena.utilizing.colors import Color
from iarena.utilizing.protocoling import (
    IPlotRenderable,
    ITextRenderable,
    as_text,
    supports_plotting,
    supports_text_rendering,
)
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator
from iarena.utilizing.structuring import (
    Factory,
    GenericEnumRegistry,
    GenericFactory,
    GenericParameter,
    GenericRegistry,
    GenericSingleton,
)
from iarena.utilizing.threadinging import ThreadCallTimeoutError, run_callable_in_worker_thread
from iarena.utilizing.Timer import Timer

__all__ = [
    "Color",
    "Factory",
    "GenericEnumRegistry",
    "GenericFactory",
    "GenericParameter",
    "GenericRegistry",
    "GenericSingleton",
    "IPlotRenderable",
    "ITextRenderable",
    "RandomGenerator",
    "ThreadCallTimeoutError",
    "Timer",
    "as_text",
    "run_callable_in_worker_thread",
    "supports_plotting",
    "supports_text_rendering",
]
