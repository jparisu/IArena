
from typing import Iterator

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex, two_player_game_change_player
from IArena.utils.decorators import override

"""
This game represents the Roman coins game.
There is a pile of n coins, and two players.
There are 2 values, min_play and max_play.
In turns, each player can take a [min_play, max_play] number of coins.
The player with no valid moves loses.
"""

class CoinsPosition(IPosition):
    """
    Represents the position of the game by counting the coins remaining.

    Attributes:
        n: The number of coins still in play.
    """

    def __init__(
            self,
            n: int,
            next_player: PlayerIndex):
        # Number of coins
        self.n = n
        # Last player that has played
        self.next_player_ = next_player

    @override
    def next_player(
            self) -> PlayerIndex:
        # Assuming players are 0 and 1, this converts 1 to 0 and viceversa
        return self.next_player_

    def __eq__(
            self,
            other: "CoinsPosition"):
        return self.n == other.n and self.next_player_ == other.next_player_

    def __str__(self):
        st = "----------------\n"
        st += f"Player: {self.next_player_}\n"
        for i in range(self.n):
            st += (" {0:3d}   === \n".format(i))
        st += "----------------\n"
        return st


class CoinsMovement(IMovement):
    """
    Represents the movement of the player in the game by counting the coins removed.

    Attributes:
        n: The number of coins removed.
    """

    def __init__(
            self,
            n: int):
        self.n = n

    def __eq__(
            self,
            other: "CoinsMovement"):
        return self.n == other.n

    def __str__(self):
        return f'{{remove: {self.n}}}'


class CoinsRules(IGameRules):

    def __init__(
            self,
            initial_position: int = 15,
            min_play: int = 1,
            max_play: int = 3):
        """
        Args:
            initial_position: The number of coins at the beginning of the game.
            min_play: The minimum number of coins that can be removed.
            max_play: The maximum number of coins that can be removed.
        """
        self.initial_position = initial_position
        self.min_play = min_play
        self.max_play = max_play

    @override
    def n_players(self) -> int:
        return 2

    @override
    def first_position(self) -> CoinsPosition:
        return CoinsPosition(
            self.initial_position,
            PlayerIndex.FirstPlayer)

    @override
    def next_position(
            self,
            movement: CoinsMovement,
            position: CoinsPosition) -> CoinsPosition:
        return CoinsPosition(
            position.n - movement.n,
            two_player_game_change_player(position.next_player))

    @override
    def possible_movements(
            self,
            position: CoinsPosition) -> Iterator[CoinsMovement]:
        return [
            CoinsMovement(x) for x in range(
                self.min_play,
                min(
                    position.n,
                    self.max_play
                ) + 1
            )
        ]

    @override
    def finished(
            self,
            position: CoinsPosition) -> bool:
        return position.n < self.min_play

    @override
    def score(
            self,
            position: CoinsPosition) -> dict[PlayerIndex, float]:
        return {
            position.next_player() : 0.0,
            two_player_game_change_player(position.next_player()) : 1.0
        }
