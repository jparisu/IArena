"""Arena loop abstraction for running one game instance."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from iarena.interfacing.IGameRules import IGameRules
from iarena.interfacing.IPlayer import IPlayer
from iarena.interfacing.IPosition import IPosition
from iarena.interfacing.ScoreBoard import ScoreBoard


class IArena(ABC):
    """Run a game loop over rules, a current position, and players.

    The arena stores one rules object, one mutable current position reference,
    and an ordered set of players. The default `play` loop:
    1. asks the current player for a movement,
    2. validates movement legality,
    3. applies the movement to get the next position,
    4. repeats until terminal state,
    5. returns final scoreboard.
    """

    def __init__(
        self,
        rules: IGameRules,
        players: Sequence[IPlayer],
        position: IPosition | None = None,
    ) -> None:
        """Initialize the arena state and validate player count."""
        expected_players = rules.n_players()
        if len(players) != expected_players:
            raise ValueError(f"number of players ({len(players)}) must match rules.n_players() ({expected_players})")
        self.rules = rules
        self.players = tuple(players)
        self.position = rules.first_position() if position is None else position
        for player_index, player in enumerate(self.players):
            player.starting_game(self.rules, player_index)

    def _play_loop(self) -> ScoreBoard:
        """Execute the default arena loop and return final/current scoreboard."""
        while not self.rules.finished(self.position):
            player_index = self.position.next_player()
            if player_index < 0 or player_index >= len(self.players):
                raise IndexError(
                    f"position returned next_player={player_index}, out of range [0, {len(self.players) - 1}]"
                )
            player = self.players[player_index]
            movement = player.play(self.position)
            if not self.rules.is_movement_possible(movement, self.position):
                raise ValueError(f"illegal movement {movement!r} for player index {player_index}")
            self.position = self.rules.next_position(movement, self.position)
        return self.rules.current_score(self.position)

    @abstractmethod
    def play(self) -> ScoreBoard:
        """Run the game and return its resulting scoreboard."""
        raise NotImplementedError
