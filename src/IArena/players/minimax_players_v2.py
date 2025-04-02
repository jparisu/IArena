
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
    def minimax(self, position: IPosition) -> Tuple[MinimaxScoreType, IMovement]:
        pass

    @pure_virtual
    def heuristic(self, position: IPosition) -> MinimaxScoreType:
        pass

    @pure_virtual
    def cache_store(self, position: IPosition, depth: int, move: IMovement, score: int):
        pass

    @pure_virtual
    def cache_get(self, position: IPosition, depth: int) -> Tuple[MinimaxScoreType, IMovement]:
        pass


class StdMinimaxPlayer(AbstractMinimaxPlayer, IPlayer):
    """
    NOTE: Assumes the players are FirstPlayer and SecondPlayer.
    FirstPlayer=MAX and SecondPlayer=MIN
    """

    def __init__(
            self,
            player: PlayerIndex = None,
            depth: int = -1,
            name: str = None):
        super().__init__(name=name)
        self.player = player
        self.depth = depth

    @override
    def play(
            self,
            position: IPosition) -> IMovement:

        res = self.minimax(position, self.depth)
        score, move = res
        return move

    @override
    def minimax(self, position: IPosition, depth: int = -1) -> Tuple[MinimaxScoreType, IMovement]:

        # Useful variables
        rules = position.get_rules()
        max_player = position.next_player() == PlayerIndex.FirstPlayer

        # Check if the score is already in the cache
        cache = self.cache_get(position, depth)
        if cache is not None:
            return cache

        # Check if the position is a terminal one
        if rules.finished(position):
            board = rules.score(position)
            score = board.get_score(PlayerIndex.FirstPlayer)
            return score, None

        # Check if the depth is 0
        if depth == 0:
            return self.heuristic(position), None

        # Calculate the score of children
        movements = rules.possible_movements(position)
        score = float('-inf') if max_player else float('inf')
        best_move = None

        for move in movements:
            next_position = rules.next_position(move, position)
            next_score, next_move = self.minimax(next_position, depth - 1)

            if max_player:
                if next_score > score:
                    score = next_score
                    best_move = move
            else:
                if next_score < score:
                    score = next_score
                    best_move = move

        # Store the score in the cache
        self.cache_store(
            position=position,
            depth=depth,
            move=best_move,
            score=score)

        return score, best_move

    @override
    def heuristic(self, position: IPosition) -> MinimaxScoreType:
        return 0

    @override
    def cache_store(self, position: IPosition, depth: int, move: IMovement, score: int):
        # Do Nothing
        pass

    @override
    def cache_get(self, position: IPosition, depth: int) -> Tuple[MinimaxScoreType, IMovement]:
        # Do Nothing
        return None


class MinimaxCachePlayer(StdMinimaxPlayer):

    def __init__(
            self,
            player: PlayerIndex = None,
            depth: int = -1,
            name: str = None):
        super().__init__(
            player=player,
            depth=depth,
            name=name)
        self.cache = {}

    @override
    def cache_store(self, position: IPosition, depth: int, move: IMovement, score: int):
        self.cache[position] = (depth, move, score)

    @override
    def cache_get(self, position: IPosition, depth: int) -> Tuple[MinimaxScoreType, IMovement]:
        if position in self.cache:
            d, m, s = self.cache[position]
            if depth < 0 or d >= depth:
                return s, m
        return None



class MinimaxPrunePlayer(StdMinimaxPlayer):

    def __init__(
            self,
            player: PlayerIndex = None,
            depth: int = -1,
            alpha: MinimaxScoreType = float('-inf'),
            beta: MinimaxScoreType = float('inf'),
            name: str = None):
        super().__init__(player, depth, name=name)
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

        # Useful variables
        rules = position.get_rules()

        # Check if the score is already in the cache
        cache_score = self.cache_get(position, depth)
        if cache_score is not None:
            return cache_score

        # Check if the position is a terminal one
        if rules.finished(position):
            s = rules.score(position)
            s = s.get_score(self.player)
            return s

        # Check if the depth is 0
        if depth == 0:
            return self.heuristic(position)

        # Calculate the score of children
        movements = rules.possible_movements(position)
        if self.player == position.next_player(): # Max player
            score = self.total_alpha
        else:
            score = self.total_beta

        any_not_pruned = False
        for i, move in enumerate(movements):

            next_position = rules.next_position(move, position)

            next_score = self.minimax(next_position, depth - 1, alpha, beta)

            if next_score is None:
                continue
            else:
                any_not_pruned = True

            if self.player == position.next_player(): # Max player
                score = max(score, next_score)
                alpha = max(alpha, next_score)
            else:
                score = min(score, next_score)
                beta = min(beta, next_score)

            if alpha >= beta:
                return score
                break

        if not any_not_pruned:
            return None

        # Calculate the score of the position
        # final_score = self.select_score(self.player == position.next_player(), scores)

        # Store the score in the cache
        self.cache_store(position, depth, score)

        return score


class MinimaxRandomConsistentPlayer(MinimaxCachePlayer):

    def __init__(
            self,
            player: PlayerIndex = None,
            depth: int = -1,
            alpha: MinimaxScoreType = float('-inf'),
            beta: MinimaxScoreType = float('inf'),
            seed: int = 0,
            name: str = None):
        super().__init__(player=player, depth=depth, alpha=alpha, beta=beta, name=name)
        self.rg = RandomGenerator(seed)

    @override
    def select_move(self, movements, scores):

        # get best score achievable
        best_score = max([s for s in scores if s is not None])
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
