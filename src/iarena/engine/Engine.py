"""Abstract base class for the game engine."""

from __future__ import annotations

from abc import ABC
from typing import Any

from iarena.game.GameRules import GameRules
from iarena.interface.Interface import Interface
from iarena.player.Player import Player


class Engine(ABC):
    """Orchestrates a complete game session.

    The engine owns the rules, the list of players, and the interface.
    Its run() method executes the game loop: requesting moves from
    players, validating them via the rules, applying them to the state,
    and firing lifecycle events on the interface.

    Subclasses may override run() to implement alternative loop
    strategies (logging, simulation, replay, …).

    Parameters
    ----------
    rules:
        The rules defining valid moves, state transitions, and outcomes.
    players:
        Ordered list of players.  Index must match state.current_player_id().
    interface:
        The I/O medium and lifecycle-event receiver for the session.
    """

    def __init__(
        self,
        rules: GameRules,
        players: list[Player],
        interface: Interface,
    ) -> None:
        self._rules = rules
        self._players = players
        self._interface = interface

    def run(self) -> Any:
        """Execute the game loop and return the final result.

        Loop skeleton:
        1. Fire on_game_start.
        2. While not terminal: fire on_turn_start, ask the active player
           for a move, validate it; if illegal fire on_invalid_move and
           retry; if legal apply it and fire on_turn_end.
        3. Fire on_game_end and return the result.

        Returns
        -------
        Any
            The game result as returned by GameRules.result.
        """
        state = self._rules.first_position()
        self._interface.on_game_start(state)

        while not self._rules.is_terminal(state):
            player = self._players[state.current_player_id()]
            self._interface.on_turn_start(state, player)

            move = player.choose_move(state)

            if not self._rules.is_legal(state, move):
                self._interface.on_invalid_move(state, player, move)
                continue

            state = self._rules.apply_move(state, move)
            self._interface.on_turn_end(state, player, move)

        result = self._rules.result(state)
        self._interface.on_game_end(state, result)
        return result
