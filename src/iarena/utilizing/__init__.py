"""Utility helpers for IArena runtime support."""

from iarena.utilizing.protocoling import (
    IPlotRenderable,
    ITextRenderable,
    as_text,
    supports_plotting,
    supports_text_rendering,
)
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator
from iarena.utilizing.threadinging import ThreadCallTimeoutError, run_callable_in_worker_thread
from iarena.utilizing.Timer import Timer

__all__ = [
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
