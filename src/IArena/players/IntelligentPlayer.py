
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


class IntelligentPlayer(IPlayer):
    """
    Minimax player

    NOTE: Assumes the players are FirstPlayer and SecondPlayer.
    FirstPlayer=MAX and SecondPlayer=MIN
    """

    def __init__(
            self,
            depth: int = -1,
            alpha: MinimaxScoreType = float('-inf'),
            beta: MinimaxScoreType = float('inf'),
            seed: int = 0,
            name: str = None):
        super().__init__(name=name)

        self.depth = depth
        self.min_alpha = alpha
        self.max_beta = beta
        self.seed = seed
        self.random_generator = RandomGenerator(seed)

        self.cache = {}


    @override
    def play(
            self,
            position: IPosition) -> IMovement:

        scores = []
        movements = position.get_rules().possible_movements(position)

        for move in movements:
            next_position = position.get_rules().next_position(move, position)
            scores.append(self.minimax(next_position, self.depth)[0])

        return self.select_move(movements, scores, self.is_max_player(position))


    def is_max_player(self, position: IPosition) -> bool:
        return position.next_player() == PlayerIndex.FirstPlayer


    def heuristic(self, position: IPosition) -> MinimaxScoreType:
        return 0


    def select_move(self, movements: list, scores: list, max_player: bool) -> IMovement:
        if max_player:
            best_score = max(scores)
        else:
            best_score = min(scores)

        best_movements = [movements[i] for i, score in enumerate(scores) if score == best_score]
        move = self.random_generator.choice(best_movements)

        return move


    def cache_store(self, position: IPosition, depth: int, score: MinimaxScoreType):
        if position in self.cache:
            d, _ = self.cache[position]
            if depth > d:
                self.cache[position] = (depth, score)
        else:
            self.cache[position] = (depth, score)


    def cache_get(self, position: IPosition, depth: int) -> MinimaxScoreType:
        if position in self.cache:
            d, s = self.cache[position]
            if d >= depth:
                return s
        return None


    def select_score(self, max_player: bool, scores: List[MinimaxScoreType]) -> MinimaxScoreType:
        # If all scores are None, return None
        real_scores = [s for s in scores if s is not None]
        if len(real_scores) == 0:
            return None
        f_player = max if max_player else min
        return f_player(real_scores)


    def cache_store(self, position: IPosition, depth: int, score: int):
        self.cache[position] = (depth, score)


    def cache_get(self, position: IPosition, depth: int) -> MinimaxScoreType:
        if position in self.cache:
            d, s = self.cache[position]
            if depth < 0 or d >= depth:
                return s
        return None


    def minimax(
            self,
            position: IPosition,
            depth: int = -1,
            alpha: float = None,
            beta: float = None) -> Tuple[MinimaxScoreType, bool]:

        # Set the alpha and beta values
        if alpha is None:
            alpha = self.min_alpha
        if beta is None:
            beta = self.max_beta

        # Useful variables
        rules = position.get_rules()
        max_player = self.is_max_player(position)

        # Check if the score is already in the cache
        cache_score = self.cache_get(position, depth)
        if cache_score is not None:
            return cache_score, False

        # Check if the position is a terminal one
        if rules.finished(position):
            board = rules.score(position)
            score = board.get_score(PlayerIndex.FirstPlayer)
            return score, False

        # Check if the depth is 0
        if depth == 0:
            return self.heuristic(position), False

        # Calculate the score of children
        score = None
        pruned = False

        # If the player is the max player
        if max_player:

            score = -math.inf

            for move in rules.possible_movements(position):
                next_position = rules.next_position(move, position)
                next_score, has_pruned = self.minimax(next_position)

                pruned = pruned or has_pruned
                score = max(score, next_score)
                alpha = max(alpha, score)

                if beta <= alpha:
                    pruned = True
                    break

        else:

            score = math.inf

            for move in rules.possible_movements(position):
                next_position = rules.next_position(move, position)
                next_score, has_pruned = self.minimax(next_position)

                pruned = pruned or has_pruned
                score = min(score, next_score)
                beta = min(beta, score)

                if beta <= alpha:
                    pruned = True
                    break


        # Store the score in the cache
        if not pruned:
            self.cache_store(position, depth, score)

        return score, pruned
