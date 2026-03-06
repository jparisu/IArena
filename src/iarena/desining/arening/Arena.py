"""Arena loop abstraction for running one game instance."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from iarena.desining.gaming.GameRules import GameRules
from iarena.desining.gaming.Position import Position
from iarena.desining.gaming.ScoreBoard import ScoreBoard
from iarena.desining.playing.Player import Player


class Arena(ABC):
    """Run a game loop over rules, a current position, and players."""

    def __init__(
        self,
        rules: GameRules,
        players: Sequence[Player],
        position: Position | None = None,
    ) -> None:
        """Initialize arena state and validate player count.

        Args:
            rules: Rules object defining game logic.
            players: Ordered players participating in the game.
            position: Optional initial position override.

        Returns:
            None.
        """
        expected_players = rules.n_players()
        if len(players) != expected_players:
            raise ValueError(f"number of players ({len(players)}) must match rules.n_players() ({expected_players})")

        self.rules = rules
        self.players = tuple(players)
        self.position = rules.first_position() if position is None else position

        for player_index, player in enumerate(self.players):
            player.starting_game(self.rules, player_index)

    def _play_loop(self) -> ScoreBoard:
        """Execute the default arena loop and return final/current scoreboard.

        Args:
            None.

        Returns:
            Scoreboard for the final position reached by the loop.
        """
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
        """Run the game and return its resulting scoreboard.

        Args:
            None.

        Returns:
            Final scoreboard after game execution.
        """
        raise NotImplementedError
