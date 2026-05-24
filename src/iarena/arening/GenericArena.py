"""Declares the generic arena abstraction shared by concrete arena engines."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol

from iarena.arening.Arena import Arena

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules
    from iarena.scoring.ScoreBoard import ScoreBoard


class GenericArena(Arena, ABC):
    """Abstract shared base for reusable arena execution workflows.

    Purpose:
        Captures common arena concerns such as loop lifecycle, turn-level
        bookkeeping, and termination checks that multiple arena variants may
        reuse.
    How it is used:
        Specialized arenas inherit from this class and provide concrete behavior
        for game-specific or mode-specific execution details.
    Why it exists:
        Avoids duplicating orchestration structure across concrete arenas and
        keeps extension points explicit.
    """

    @abstractmethod
    def _execute_turn(self) -> None:
        """Execute one arena turn.

        What it does:
            Defines the per-turn execution hook of the arena loop.
        How it works:
            Concrete arenas should advance the match state by one valid turn,
            including action collection and transition application.
        Args:
            None.
        Returns:
            None: Updates internal arena state for the next loop iteration.
        """
        raise NotImplementedError

    @abstractmethod
    def _check_timeout(self) -> bool:
        """Check whether the global time budget has been exhausted.

        What it does:
            Defines timeout validation for the current match execution.
        How it works:
            Concrete arenas should compare elapsed time against configured limits.
        Args:
            None.
        Returns:
            bool: ``True`` when timeout stop condition is met, otherwise ``False``.
        """
        raise NotImplementedError

    @abstractmethod
    def _check_score_limit(self) -> bool:
        """Check whether score-limit termination has been reached.

        What it does:
            Defines score-based stop-condition validation.
        How it works:
            Concrete arenas should inspect current scoreboard values against
            configured lower/upper boundaries.
        Args:
            None.
        Returns:
            bool: ``True`` when score limits require finishing the match.
        """
        raise NotImplementedError

    @abstractmethod
    def _check_max_turns(self) -> bool:
        """Check whether the turn-count budget has been exhausted.

        What it does:
            Defines turn-budget validation used by the game loop.
        How it works:
            Concrete arenas should compare current turn count against maximum turns.
        Args:
            None.
        Returns:
            bool: ``True`` when no more turns are allowed, otherwise ``False``.
        """
        raise NotImplementedError

    @abstractmethod
    def _store_logs(self, last_movement: Movement) -> None:
        """Persist movement and/or state data for debugging or replay.

        What it does:
            Defines the logging hook called after each executed movement.
        How it works:
            Concrete arenas decide what data is recorded and where it is stored.
        Args:
            last_movement (Movement): Most recent movement executed in the loop.
        Returns:
            None: Produces side effects by persisting log information.
        """
        raise NotImplementedError

    def _game_loop(self) -> ScoreBoard:
        """Run the main loop until a termination condition is reached.

        What it does:
            Defines the reusable core loop contract shared by concrete arenas.
        How it works:
            Implementations should repeatedly execute turns, evaluate stop
            conditions, and return the final scoreboard.
        Args:
            None.
        Returns:
            ScoreBoard: Score snapshot produced at loop termination.
        Raises:
            RuntimeError: If required arena state (`_rules` and `_position`) is
                missing when the loop terminates.
        """

        while True:
            if self._check_timeout():
                raise TimeoutError(f"Match execution exceeded time limit of {self._max_total_time_s} seconds.")

            elif self._check_score_limit():
                raise StopIteration("Score limit reached, finishing match.")

            elif self._check_max_turns():
                raise StopIteration("Max turns reached, finishing match.")

            self._execute_turn()
            self._turn_count += 1

            should_store_logs = bool(getattr(self, "_should_store_logs", False))
            if should_store_logs:
                last_movement = getattr(self, "_last_movement", None)
                if last_movement is not None:
                    self._store_logs(last_movement)

            if self._rules.is_finished(self._current_position):
                break

        return self._rules.get_score(self._current_position)


class ExecuteTurnProtocol(Protocol):
    """Protocol for arena implementations that execute one turn."""

    def _execute_turn(self) -> None:
        """Execute one arena turn."""


class TimeoutCheckProtocol(Protocol):
    """Protocol for arena implementations that check timeout termination."""

    def _check_timeout(self) -> bool:
        """Return whether timeout termination has been reached."""


class ScoreLimitCheckProtocol(Protocol):
    """Protocol for arena implementations that check score-limit termination."""

    def _check_score_limit(self) -> bool:
        """Return whether score-limit termination has been reached."""


class MaxTurnsCheckProtocol(Protocol):
    """Protocol for arena implementations that check turn-budget termination."""

    def _check_max_turns(self) -> bool:
        """Return whether max-turn termination has been reached."""


class StoreLogsProtocol(Protocol):
    """Protocol for arena implementations that persist turn logs."""

    def _store_logs(self, last_movement: Movement) -> None:
        """Persist the provided movement in arena logs."""
