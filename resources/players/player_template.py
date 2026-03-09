"""Template module for custom loadable players."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from iarena.playing.Player import Player

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules
    from iarena.playing.PlayerIndex import PlayerIndex

AUTHORS = [
    "Jon Doe",
    "Jane Smith",
]


class MyPlayer(Player):
    def play(self, pos: Position) -> Movement:
        # Return a random movement from the iterator of legal movements.
        return random.choice(list(pos.get_rules().possible_movements(pos)))

    def authors(self) -> list[str]:
        return AUTHORS

    def name(self) -> str:
        return "my-player"

    def starting_game(self, rules: Rules, player_index: PlayerIndex) -> None:
        pass


# Variable declaration for player instance.
PLAYER = MyPlayer()
