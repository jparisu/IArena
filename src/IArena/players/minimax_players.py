
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

class AbstractMinimaxPlayer():

    @pure_virtual
    def minimax(self, position: IPosition) -> MinimaxScoreType:
        pass

    @pure_virtual
    def heuristic(self, position: IPosition) -> MinimaxScoreType:
        pass

    @pure_virtual
    def select_move(self, movements: List[IMovement], scores: List[MinimaxScoreType], position: IPosition = None) -> IMovement:
        pass

    @pure_virtual
    def cache_store(self, position: IPosition, depth: int, alpha: MinimaxScoreType, beta: MinimaxScoreType, score: MinimaxScoreType):
        pass

    @pure_virtual
    def cache_get(self, position: IPosition, depth: int, alpha: MinimaxScoreType, beta: MinimaxScoreType) -> MinimaxScoreType:
        pass


class StdMinimaxPlayer(AbstractMinimaxPlayer, IPlayer):

    def __init__(
            self,
            depth: int = -1,
            name: str = None):
        super().__init__(name=name)
        self.depth = depth

    @override
    def play(
            self,
            position: IPosition) -> IMovement:

        scores = []
        movements = position.get_rules().possible_movements(position)

        for move in movements:
            next_position = position.get_rules().next_position(move, position)
            scores.append(self.minimax(next_position, self.depth))

        return self.select_move(movements, scores, position)

    @override
    def minimax(self, position: IPosition, depth: int = -1) -> MinimaxScoreType:

        # Useful variables
        rules = position.get_rules()
        max_playing = self.is_max_playing(position)

        # Check if the score is already in the cache
        cache_score = self.cache_get(position, depth)
        if cache_score is not None:
            return cache_score

        # Check if the position is a terminal one
        if rules.finished(position):
            s = rules.score(position)
            return s.get_score(self.max_player())

        # Check if the depth is 0
        if depth == 0:
            return self.heuristic(position)

        # Calculate the score of children
        movements = rules.possible_movements(position)
        if max_playing: # Max player
            score = math.inf
        else:
            score = -math.inf

        for move in movements:

            next_position = rules.next_position(move, position)
            next_score = self.minimax(next_position, depth - 1)

            if max_playing: # Max player
                score = max(score, next_score)
            else:
                score = min(score, next_score)

        # Store the score in the cache
        self.cache_store(position, depth, score)

        return score

    @override
    def heuristic(self, position: IPosition) -> MinimaxScoreType:
        return 0

    @override
    def select_move(self, movements: list, scores: list, position: IPosition) -> IMovement:
        if self.is_max_playing(position):
            best_value = max([s for s in scores if s is not None])
        else:
            best_value = min([s for s in scores if s is not None])
        return movements[scores.index(best_value)]


    @override
    def cache_store(
            self,
            position: IPosition,
            score: MinimaxScoreType,
            depth: int = None,
            alpha: MinimaxScoreType = None,
            beta: MinimaxScoreType = None):
        # Do Nothing
        pass

    @override
    def cache_get(
            self,
            position: IPosition,
            depth: int = None,
            alpha: MinimaxScoreType = None,
            beta: MinimaxScoreType = None) -> MinimaxScoreType:
        # Do Nothing
        return None

    def max_player(self) -> PlayerIndex:
        return PlayerIndex.FirstPlayer

    def is_max_playing(self, position: IPosition) -> bool:
        return position.next_player() == self.max_player()


class MinimaxPrunePlayer(StdMinimaxPlayer):

    def __init__(
            self,
            depth: int = -1,
            alpha: MinimaxScoreType = float('-inf'),
            beta: MinimaxScoreType = float('inf'),
            name: str = None):
        super().__init__(depth, name=name)
        self.total_alpha = alpha
        self.total_beta = beta

    @override
    def minimax(
            self,
            position: IPosition,
            depth: int = -1,
            alpha: float = None,
            beta: float = None) -> MinimaxScoreType:

        # If alpha and beta are not provided, use the total ones
        alpha = alpha if alpha is not None else self.total_alpha
        beta = beta if beta is not None else self.total_beta

        initial_alpha = alpha
        initial_beta = beta

        # Useful variables
        rules = position.get_rules()
        max_playing = self.is_max_playing(position)

        # Check if the score is already in the cache
        cache_score = self.cache_get(
            position=position,
            depth=depth,
            alpha=alpha,
            beta=beta,
        )
        if cache_score is not None:
            return cache_score

        # Check if the position is a terminal one
        if rules.finished(position):
            board = rules.score(position)
            s = board.get_score(self.max_player())
            return s

        # Check if the depth is 0
        if depth == 0:
            return self.heuristic(position)

        # Calculate the score of children
        movements = rules.possible_movements(position)
        if max_playing: # Max player
            score = self.total_alpha
        else:
            score = self.total_beta

        for i, move in enumerate(movements):

            next_position = rules.next_position(move, position)
            next_score = self.minimax(next_position, depth - 1, alpha, beta)

            if max_playing: # Max player
                score = max(score, next_score)
                alpha = max(alpha, next_score)
            else:
                score = min(score, next_score)
                beta = min(beta, next_score)

            if alpha >= beta:
                break

        # Store the score in the cache
        self.cache_store(
            position=position,
            score=score,
            depth=depth,
            alpha=initial_alpha,
            beta=initial_beta,
        )

        return score



class MinimaxCachePlayer(MinimaxPrunePlayer):

    def __init__(
            self,
            depth: int = -1,
            alpha: MinimaxScoreType = float('-inf'),
            beta: MinimaxScoreType = float('inf'),
            name: str = None):
        super().__init__(
            depth=depth,
            alpha=alpha,
            beta=beta,
            name=name)
        self.cache = {}

    @override
    def cache_store(
            self,
            position: IPosition,
            score: MinimaxScoreType,
            depth: int,
            alpha: MinimaxScoreType,
            beta: MinimaxScoreType):
        # This assumes cache store will never be called if the value is already in the cache
        self.cache[position] = (depth, alpha, beta, score)

    @override
    def cache_get(
            self,
            position: IPosition,
            depth: int,
            alpha: MinimaxScoreType,
            beta: MinimaxScoreType) -> MinimaxScoreType:
        if position in self.cache:
            d, a, b, s = self.cache[position]
            if d >= depth and a <= alpha and b >= beta:
                return s
        return None


class MinimaxRandomConsistentPlayer(MinimaxCachePlayer):

    def __init__(
            self,
            depth: int = -1,
            alpha: MinimaxScoreType = float('-inf'),
            beta: MinimaxScoreType = float('inf'),
            seed: int = 0,
            name: str = None):
        super().__init__(depth=depth, alpha=alpha, beta=beta, name=name)
        self.rg = RandomGenerator(seed)

    @override
    def select_move(self, movements: list, scores: list, position: IPosition) -> IMovement:

        # get the best score
        if self.is_max_playing(position):
            best_score = max([s for s in scores if s is not None])
        else:
            best_score = min([s for s in scores if s is not None])

        # get movements with best score
        best_movements = [movements[i] for i, score in enumerate(scores) if score == best_score]
        # select a random one
        move = self.rg.choice(best_movements)

        return move


class MinimaxRandomMatchConsistentPlayer(MinimaxRandomConsistentPlayer):

    @override
    def starting_game(
            self,
            rules: IGameRules,
            player_index: int):
        super().starting_game(rules, player_index)
        self.rg.reset_seed()
