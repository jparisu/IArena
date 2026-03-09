"""Defines a configured generic arena base with shared runtime wiring."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from iarena.arening.GenericArena import GenericArena
from iarena.scoring.Score import Score
from iarena.utilizing.timing.Timer import Timer
from iarena.visualizing.EmptyView import EmptyView

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Rules import Rules
    from iarena.playing.Player import Player
    from iarena.scoring.ScoreBoard import ScoreBoard
    from iarena.visualizing.View import View


class ConfiguredArenaBase(GenericArena):
    """Base class storing shared arena execution state and setup hooks.

    Purpose:
        Centralize constructor wiring and runtime helper methods that are shared
        by hook-specific arena subclasses.
    How it is used:
        Behavior classes inherit from this class and implement one of the arena
        extension hooks declared in `GenericArena`.
    Why it exists:
        Keeps hook implementations independent while preserving one canonical
        setup flow for configured arenas.
    """

    _CONFIGURED_CLASS_CACHE: dict[tuple[bool, bool, bool], type[ConfiguredArenaBase]] = {}

    @classmethod
    def create_configured_arena_class(
        cls,
        max_turns: int | None,
        score_limits: tuple[Score, Score] | None,
        store_logs: bool,
        max_turn_time_s: float | None = None,
    ) -> type[ConfiguredArenaBase]:
        """Build a concrete arena class matching enabled/disabled constraints.

        Args:
            max_turns: Turn limit configuration. `None` disables max-turn checks.
            score_limits: Score limit configuration. `None` disables score bounds.
            store_logs: Whether logging behavior should persist turn logs.

        Returns:
            type[ConfiguredArenaBase]: Arena class composed from behavior mixins.
        """
        _ = cls
        has_max_turns_limit = max_turns is not None
        has_score_limit = score_limits is not None

        cache_key = (has_max_turns_limit, has_score_limit, store_logs)
        cached_class = ConfiguredArenaBase._CONFIGURED_CLASS_CACHE.get(cache_key)
        if cached_class is not None:
            return cached_class

        from iarena.arening.behaviors.LogsStoringArena import LogsStoringArena
        from iarena.arening.behaviors.MaxTurnsCheckingArena import MaxTurnsCheckingArena
        from iarena.arening.behaviors.NoLogsArena import NoLogsArena
        from iarena.arening.behaviors.NoMaxTurnsArena import NoMaxTurnsArena
        from iarena.arening.behaviors.NoScoreLimitArena import NoScoreLimitArena
        from iarena.arening.behaviors.ScoreLimitCheckingArena import ScoreLimitCheckingArena
        from iarena.arening.behaviors.TimeoutCheckingArena import TimeoutCheckingArena
        from iarena.arening.behaviors.WorkerExecuteTurnArena import WorkerExecuteTurnArena
        from iarena.arening.behaviors.DirectExecuteTurnArena import DirectExecuteTurnArena

        max_turns_behavior = MaxTurnsCheckingArena if has_max_turns_limit else NoMaxTurnsArena
        score_limit_behavior = ScoreLimitCheckingArena if has_score_limit else NoScoreLimitArena
        logs_behavior = LogsStoringArena if store_logs else NoLogsArena
        worker_behavior = WorkerExecuteTurnArena if max_turn_time_s is not None and max_turn_time_s > 0 else DirectExecuteTurnArena

        arena_class_name = (
            "ConfiguredArena_"
            f"{'MaxTurns' if has_max_turns_limit else 'NoMaxTurns'}_"
            f"{'ScoreLimit' if has_score_limit else 'NoScoreLimit'}_"
            "Timeout_"
            f"{'Logs' if store_logs else 'NoLogs'}"
        )
        arena_class = type(
            arena_class_name,
            (
                worker_behavior,
                TimeoutCheckingArena,
                score_limit_behavior,
                max_turns_behavior,
                logs_behavior,
            ),
            {},
        )
        ConfiguredArenaBase._CONFIGURED_CLASS_CACHE[cache_key] = arena_class
        return arena_class

    def __init__(
        self,
        max_turns: int | None,
        max_turn_time_s: float | None,
        max_total_time_s: float | None,
        score_limits: tuple[Score, Score] | None,
        store_logs: bool,
    ) -> None:
        """Initialize one configured arena runtime.

        Args:
            max_turns: Maximum turn budget for the match. `None` means unlimited.
            max_turn_time_s: Per-turn timeout budget in seconds. `None` means unlimited.
            max_total_time_s: Global timeout budget in seconds. `None` means unlimited.
            score_limits: Inclusive lower and upper score thresholds.
                `None` means no score-based bounds.
            store_logs: Whether turn-level logs should be persisted.

        Returns:
            None.
        """
        self._max_turns = max_turns
        self._max_turn_time_s = max_turn_time_s
        self._max_total_time_s = max_total_time_s
        self._score_limits = score_limits
        self._should_store_logs = store_logs

    def play(self, rules: Rules, players: list[Player], view: View | None = None) -> ScoreBoard:
        """Play a match and return the final scoreboard.

        Args:
            rules: Rules engine for match progression and scoring.
            players: Ordered players that will participate in the match.
            view: Optional view associated with this execution. When omitted,
                `EmptyView` is used.

        Returns:
            ScoreBoard: Final scoreboard after loop termination.
        """
        self._rules = rules
        self._players = list(players)
        self._view = EmptyView() if view is None else view

        self._timer = Timer(start_activated=True)
        self._turn_count = 0
        self._timed_out = False
        self._current_position = self._rules.first_position()
        self._last_movement: Movement | None = None
        self._logs: list[dict[str, Any]] = []

        self._validate_player_count()
        self._bind_view_players()
        self._notify_starting_game()
        return self._game_loop()

    def _validate_player_count(self) -> None:
        """Validate that configured players match rule requirements.

        Returns:
            None.

        Raises:
            ValueError: If player count does not satisfy `rules.n_players()`.
        """
        required_players = self._rules.n_players()
        if len(self._players) != required_players:
            raise ValueError(
                "Number of players does not match rules requirements: "
                f"expected {required_players}, got {len(self._players)}.",
            )

    def _bind_view_players(self) -> None:
        """Bind configured players to the view when it exposes a players field.

        Returns:
            None.
        """
        if hasattr(self._view, "players"):
            self._view.players = list(self._players)

    def _notify_starting_game(self) -> None:
        """Notify players about game start when they expose `starting_game`.

        Returns:
            None.
        """
        from iarena.playing.PlayerIndex import PlayerIndex

        for player_index, player in enumerate(self._players):
            starting_game = getattr(player, "starting_game", None)
            if callable(starting_game):
                starting_game(self._rules, PlayerIndex(player_index))
