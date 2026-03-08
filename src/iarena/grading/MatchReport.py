"""Defines the result snapshot structure produced by one match run."""

from __future__ import annotations

from typing import Any

from iarena.scoring.Score import Score


class MatchReport:
    """Result snapshot of a single match execution.

    Purpose:
        Hold the measured outcome and metadata for one completed match.
    How it is used:
        Trial and exam orchestration components aggregate these reports to
        compute summary scores and emit grading evidence.
    Why it exists:
        Provides a stable, typed contract for persisting and exchanging
        per-match results across grading layers.
    """

    moves: int
    total_time_s: float
    score: Score
    messages: dict[str, Any]
