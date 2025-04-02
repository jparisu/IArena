
import random
import math
from typing import Tuple, List

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IPlayer import IPlayer
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.interfaces.ScoreBoard import ScoreBoard
from IArena.utils.decorators import override, pure_virtual
from IArena.utils.RandomGenerator import RandomGenerator

MinimaxScoreType = float

class CacheMinimaxPlayer(IPlayer):
    """
    NOTE: Assumes the players are FirstPlayer and SecondPlayer.
    FirstPlayer=MAX and SecondPlayer=MIN
    """

    def __init__(
            self,
            name: str = None):
        super().__init__(name=name)
        self.cache = {}

    @override
    def play(
            self,
            position: IPosition) -> IMovement:
        return self.minimax(position)[1]


    @override
    def minimax(self, position: IPosition) -> Tuple[MinimaxScoreType, IMovement]:

        # Useful variables
        rules = position.get_rules()
        max_player = position.next_player() == PlayerIndex.FirstPlayer

        # Check if the position is a terminal one
        if rules.finished(position):
            board = rules.score(position)
            score = board.get_score(PlayerIndex.FirstPlayer)
            return score, None

        if position in self.cache:
            return self.cache[position]

        if max_player:
            score = float('-inf')
            for move in rules.possible_movements(position):
                next_position = rules.next_position(move, position)
                next_score, _ = self.minimax(next_position)
                if next_score > score:
                    score = next_score
                    best_move = move

        else:
            score = float('inf')
            for move in rules.possible_movements(position):
                next_position = rules.next_position(move, position)
                next_score, _ = self.minimax(next_position)
                if next_score < score:
                    score = next_score
                    best_move = move

        self.cache[position] = (score, best_move)

        return score, best_move
