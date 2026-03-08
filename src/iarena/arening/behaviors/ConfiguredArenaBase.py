"""Defines a configured generic arena base with shared runtime wiring."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from iarena.arening.GenericArena import GenericArena
from iarena.gaming.Movement import Movement
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.scoring.Score import Score
from iarena.utilizing.timing.Timer import Timer

if TYPE_CHECKING:
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

    def __init__(
        self,
        rules: Rules,
        view: View,
        players: Sequence[Player],
        max_turns: int,
        max_turn_time_s: float,
        max_total_time_s: float,
        score_limits: tuple[Score, Score],
        store_logs: bool,
    ) -> None:
        """Initialize one configured arena runtime.

        Args:
            rules: Rules engine for match progression and scoring.
            view: View frontend associated with this execution.
            players: Ordered participants in the match.
            max_turns: Maximum turn budget for the match.
            max_turn_time_s: Per-turn timeout budget in seconds.
            max_total_time_s: Global timeout budget in seconds.
            score_limits: Inclusive lower and upper score thresholds.
            store_logs: Whether turn-level logs should be persisted.

        Returns:
            None.
        """
        self._rules = rules
        self._view = view
        self._players = list(players)
        self._max_turns = max_turns
        self._max_turn_time_s = max_turn_time_s
        self._max_total_time_s = max_total_time_s
        self._score_limits = score_limits
        self._should_store_logs = store_logs

        self._timer = Timer(start_activated=True)
        self._turn_count = 0
        self._timed_out = False
        self._position = self._rules.first_position()
        self._last_movement: Movement | None = None
        self._logs: list[dict[str, Any]] = []

        self._validate_player_count()
        self._bind_view_players()
        self._notify_starting_game()

    def play(self, rules: Rules, players: list[Player], view: View) -> ScoreBoard:
        """Play a match and return the final scoreboard.

        Args:
            rules: Expected rules instance bound to this arena.
            players: Expected ordered player collection bound to this arena.
            view: Expected view instance bound to this arena.

        Returns:
            ScoreBoard: Final scoreboard after loop termination.

        Raises:
            ValueError: If call arguments do not match the arena configuration.
        """
        if rules is not self._rules:
            raise ValueError("The provided `rules` object does not match this arena configuration.")
        if list(players) != self._players:
            raise ValueError("The provided `players` do not match this arena configuration.")
        if view is not self._view:
            raise ValueError("The provided `view` object does not match this arena configuration.")
        return self._game_loop()

    def _validate_player_count(self) -> None:
        """Validate that configured players match rule requirements.

        Args:
            None.

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

        Args:
            None.

        Returns:
            None.
        """
        if hasattr(self._view, "players"):
            self._view.players = list(self._players)

    def _notify_starting_game(self) -> None:
        """Notify players about game start when they expose `starting_game`.

        Args:
            None.

        Returns:
            None.
        """
        for player_index, player in enumerate(self._players):
            starting_game = getattr(player, "starting_game", None)
            if callable(starting_game):
                starting_game(self._rules, PlayerIndex(player_index))
