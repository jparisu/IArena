"""Declares the arena factory responsible for selecting arena implementations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from iarena.arening.behaviors.ConfiguredArenaBase import ConfiguredArenaBase

if TYPE_CHECKING:
    from iarena.arening.Arena import Arena
    from iarena.scoring.Score import Score


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
        max_turns: int | None = None,
        max_turn_time_s: float | None = None,
        max_total_time_s: float | None = None,
        score_limits: tuple[Score, Score] | None = None,
        store_logs: bool = False,
    ) -> Arena:
        """Create a compatible arena instance for the provided execution setup.

        What it does:
            Defines the central factory entrypoint for arena selection and creation.
        How it works:
            Concrete logic inspects execution limits to compose and instantiate
            the best available arena strategy.
        Args:
            max_turns (int | None): Maximum number of turns allowed in the match.
                `None` means no turn-count limit.
            max_turn_time_s (float | None): Maximum time allowed per turn in
                seconds. `None` means no per-turn timeout.
            max_total_time_s (float | None): Maximum total match duration in
                seconds. `None` means no global timeout.
            score_limits (tuple[Score, Score] | None): Inclusive lower and upper
                score thresholds used as stop conditions. `None` means no score
                bounds.
            store_logs (bool): Whether per-turn logs should be persisted.
        Returns:
            Arena: Arena instance configured for the provided execution context.
        Raises:
            ValueError: If numeric configuration values are invalid.
        """
        _ = cls
        if max_turns is not None and max_turns <= 0:
            raise ValueError("`max_turns` must be strictly positive.")
        if max_turn_time_s is not None and max_turn_time_s <= 0:
            raise ValueError("`max_turn_time_s` must be strictly positive.")
        if max_total_time_s is not None and max_total_time_s <= 0:
            raise ValueError("`max_total_time_s` must be strictly positive.")
        if score_limits is not None and score_limits[0] > score_limits[1]:
            raise ValueError("`score_limits` must be an ordered pair `(low, high)` with `low <= high`.")

        configured_arena_class = ConfiguredArenaBase.create_configured_arena_class(
            max_turns=max_turns,
            score_limits=score_limits,
            store_logs=store_logs,
            max_turn_time_s=max_turn_time_s,
        )
        return configured_arena_class(
            max_turns=max_turns,
            max_turn_time_s=max_turn_time_s,
            max_total_time_s=max_total_time_s,
            score_limits=score_limits,
            store_logs=store_logs,
        )
