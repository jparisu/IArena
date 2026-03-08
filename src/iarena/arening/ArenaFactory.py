"""Declares the arena factory responsible for selecting arena implementations."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from .DefaultArena import DefaultArena

if TYPE_CHECKING:
    from iarena.gaming.Rules import Rules
    from iarena.playing.Player import Player
    from iarena.scoring.Score import Score
    from iarena.visualizing.View import View

    from .Arena import Arena


class ArenaFactory:
    """Factory placeholder that centralizes arena creation strategy.

    Purpose:
        Provides a single place to map runtime requirements to an appropriate
        arena implementation.
    How it is used:
        Application entrypoints and grading flows will ask this factory for an
        arena instance instead of instantiating concrete classes directly.
    Why it exists:
        Reduces coupling between callers and specific arena classes while
        enabling future extension of arena policies.
    """

    @classmethod
    def create_arena(
        cls,
        rules: Rules,
        view: View,
        players: Sequence[Player],
        max_turns: int,
        max_turn_time_s: float,
        max_total_time_s: float,
        score_limits: tuple[Score, Score],
        store_logs: bool,
    ) -> Arena:
        """Create a compatible arena instance for the provided execution setup.

        What it does:
            Defines the central factory entrypoint for arena selection and creation.
        How it works:
            Concrete logic is expected to inspect rules, players, and execution
            limits to choose and instantiate the best available arena strategy.
        Args:
            rules (Rules): Rules engine that defines game behavior.
            view (View): Frontend used to render state and capture human input.
            players (Sequence[Player]): Ordered participants of the match.
            max_turns (int): Maximum number of turns allowed in the match.
            max_turn_time_s (float): Maximum time allowed per turn in seconds.
            max_total_time_s (float): Maximum total match duration in seconds.
            score_limits (tuple[Score, Score]): Inclusive lower and upper score
                thresholds used as stop conditions.
            store_logs (bool): Whether per-turn logs should be persisted.
        Returns:
            Arena: Arena instance configured for the provided execution context.
        Raises:
            ValueError: If numeric configuration values are invalid.
        """
        _ = cls
        if max_turns <= 0:
            raise ValueError("`max_turns` must be strictly positive.")
        if max_turn_time_s <= 0:
            raise ValueError("`max_turn_time_s` must be strictly positive.")
        if max_total_time_s <= 0:
            raise ValueError("`max_total_time_s` must be strictly positive.")
        if score_limits[0] > score_limits[1]:
            raise ValueError("`score_limits` must be an ordered pair `(low, high)` with `low <= high`.")

        return DefaultArena(
            rules=rules,
            view=view,
            players=players,
            max_turns=max_turns,
            max_turn_time_s=max_turn_time_s,
            max_total_time_s=max_total_time_s,
            score_limits=score_limits,
            store_logs=store_logs,
        )
