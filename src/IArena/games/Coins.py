
from typing import Iterator, List
from copy import deepcopy

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex, two_player_game_change_player
from IArena.utils.decorators import override
from IArena.interfaces.ScoreBoard import ScoreBoard

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
            rules: "CoinsRules",
            coins: List[float],
            next_player: PlayerIndex,
            current_score: ScoreBoard = ScoreBoard()):
        super().__init__(rules)

        # Number of coins
        self.coins_ = coins

        # Player to play next
        self.next_player_ = next_player

        # Score of the game
        self.score_ = current_score

    def __len__(self) -> int:
        return self.n

    @override
    def next_player(
            self) -> PlayerIndex:
        # Assuming players are 0 and 1, this converts 1 to 0 and viceversa
        return self.next_player_

    def coins(self) -> List[float]:
        return deepcopy(self.coins_)

    def current_score(self) -> ScoreBoard:
        return deepcopy(self.score_)

    def __eq__(
            self,
            other: "CoinsPosition") -> bool:
        return self.coins_ == other.coins_ and self.next_player_ == other.next_player_ and self.score_ == other.score_

    def __str__(self) -> str:
        return f"{self.score_} {{{self.next_player_}}}" + [f"{x:2d}" for x in self.coins_]

    def __len__(self) -> int:
        return len(self.coins_)

    def __hash__(self):
        l = self.coins_ + [self.next_player_] + [hash(self.score_)]
        return hash(tuple(l))


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
            other: "CoinsMovement") -> bool:
        return self.n == other.n

    def __str__(self) -> str:
        return f'{{{self.n}}}'


class CoinsRules(IGameRules):

    def __init__(
            self,
            initial_position_last_coin: int = 100,
            initial_position: List[float] = None,
            min_play: int = 1,
            max_play: int = 3,
            n_players: int = 2):
        """
        Args:
            initial_position: The number of coins at the beginning of the game.
            min_play: The minimum number of coins that can be removed.
            max_play: The maximum number of coins that can be removed.
        """
        if initial_position is None:
            initial_position = [1] + [0] * (initial_position_last_coin - 1)
        self.initial_position_ = initial_position

        self.min_play_ = min_play
        self.max_play_ = max_play

        self.n_players_ = n_players

    def min_play(self) -> int:
        """Minimum number of coins that can be removed in a turn."""
        return self.min_play_

    def max_play(self) -> int:
        """Maximum number of coins that can be removed in a turn."""
        return self.max_play_

    @override
    def n_players(self) -> int:
        return self.n_players_

    @override
    def first_position(self) -> CoinsPosition:
        return CoinsPosition(
            rules=self,
            coins=self.initial_position_,
            next_player=PlayerIndex.FirstPlayer)

    @override
    def next_position(
            self,
            movement: CoinsMovement,
            position: CoinsPosition) -> CoinsPosition:
        # Check if the movement is valid
        if movement.n > len(position.coins()):
            raise ValueError(f"Invalid movement {movement}: removing more coins than available.")

        # Calculate new score
        score = position.current_score()
        value_taken = sum(position.coins()[-movement.n:])
        score.add_score(position.next_player(), value_taken)

        # Calculate next player
        next_player = (position.next_player() + 1) % self.n_players()
        # Calculate new position
        coins = list(position.coins()[:-movement.n])

        return CoinsPosition(
            rules=self,
            coins=coins,
            next_player=next_player,
            current_score=score)

    @override
    def possible_movements(
            self,
            position: CoinsPosition) -> Iterator[CoinsMovement]:
        return [
            CoinsMovement(x) for x in range(
                self.min_play(),
                min(
                    len(position),
                    self.max_play()
                ) + 1
            )
        ]

    @override
    def finished(
            self,
            position: CoinsPosition) -> bool:
        return len(position) < self.min_play()

    @override
    def score(
            self,
            position: CoinsPosition) -> ScoreBoard:
        # Get the scores and distribute them so they sum up 0
        board = position.current_score()
        total_score = sum(board.score)

        scores = ScoreBoard()
        for i, s in enumerate(board.score):
            scores.add_score(i, s - (total_score / 2))
        return scores
