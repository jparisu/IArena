"""Declares shared limits and constraints for a single match execution."""

from __future__ import annotations

from dataclasses import dataclass

from iarena.scoring.Score import Score


@dataclass
class MatchConfiguration:
    """Generic match execution limits shared across game trials.

    Purpose:
        Capture the timeout, turn, and score bound parameters for one match.
    How it is used:
        Trial-level orchestration objects provide this configuration to each
        match execution so all repetitions run under the same constraints.
    Why it exists:
        Centralizes operational limits in one typed object to keep grading
        runs reproducible and consistent.
    """

    move_timeout_s: float
    total_timeout_s: float
    max_turns: int
    score_limits: tuple[Score, Score]
