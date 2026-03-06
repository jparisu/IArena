"""Naming utilities."""

from __future__ import annotations

import string


def naming_convention(name: str) -> str:
    """Normalize a name to lowercase alphanumeric tokens without spaces."""
    normalized = name.lower()
    normalized = normalized.translate(str.maketrans("", "", string.punctuation))
    normalized = normalized.replace(" ", "")
    return normalized


def Naming_convention(name: str) -> str:
    """Backward-compatible alias for :func:`naming_convention`."""
    return naming_convention(name)


__all__ = ["Naming_convention", "naming_convention"]
