
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
    def select_move(self, movements: List[IMovement], scores: List[MinimaxScoreType]) -> IMovement:
        pass

    @pure_virtual
    def cache_store(self, position: IPosition, depth: int, score: int):
        pass

    @pure_virtual
    def cache_get(self, position: IPosition, depth: int) -> MinimaxScoreType:
        pass

    @pure_virtual
    def select_score(self, scores: List[MinimaxScoreType]) -> MinimaxScoreType:
        pass

    @pure_virtual
    def value_from_score(self, score: ScoreBoard) -> MinimaxScoreType:
        pass


class StdMinimaxPlayer(AbstractMinimaxPlayer, IPlayer):

    def __init__(
            self,
            player: PlayerIndex = None,
            depth: int = -1):
        self.player = player
        self.depth = depth

    @override
    def starting_game(
            self,
            rules: IGameRules,
            player_index: int):
        self.player = player_index

    @override
    def play(
            self,
            position: IPosition) -> IMovement:

        scores = []
        movements = position.get_rules().possible_movements(position)

        for move in movements:
            next_position = position.get_rules().next_position(move, position)
            scores.append(self.minimax(next_position, self.depth))

        # print("Player: ", self.player, "Scores: ", scores)
        return self.select_move(movements, scores)

    @override
    def minimax(self, position: IPosition, depth: int = -1) -> MinimaxScoreType:

        # Useful variables
        rules = position.get_rules()

        # Check if the score is already in the cache
        cache_score = self.cache_get(position, depth)
        if cache_score is not None:
            return cache_score

        # Check if the position is a terminal one
        if rules.finished(position):
            s = rules.score(position)
            return s.get_score(self.player)

        # Check if the depth is 0
        if depth == 0:
            return self.heuristic(position)

        # Calculate the score of children
        movements = rules.possible_movements(position)
        scores = []
        for move in movements:
            next_position = rules.next_position(move, position)
            next_score = self.minimax(next_position, depth - 1)
            scores.append(next_score)

        # Calculate the score of the position
        final_score = self.select_score(self.player == position.next_player(), scores)

        # Store the score in the cache
        self.cache_store(position, depth, final_score)

        return final_score

    @override
    def heuristic(self, position: IPosition) -> MinimaxScoreType:
        return 0

    @override
    def select_move(self, movements: list, scores: list) -> IMovement:
        return movements[scores.index(max(scores))]

    @override
    def cache_store(self, position: IPosition, depth: int, score: MinimaxScoreType):
        # Do Nothing
        pass

    @override
    def cache_get(self, position: IPosition, depth: int) -> MinimaxScoreType:
        # Do Nothing
        return None

    @override
    def select_score(self, max_player: bool, scores: List[MinimaxScoreType]) -> MinimaxScoreType:
        f_player = max if max_player else min
        return f_player(scores)

    @override
    def value_from_score(self, score: ScoreBoard) -> MinimaxScoreType:
        return score[self.player]


class MinimaxPrunePlayer(StdMinimaxPlayer):

    def __init__(
            self,
            player: PlayerIndex = None,
            depth: int = -1,
            alpha: MinimaxScoreType = float('-inf'),
            beta: MinimaxScoreType = float('inf')):
        super().__init__(player, depth)
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
            return s.get_score(self.player)

        # Check if the depth is 0
        if depth == 0:
            return self.heuristic(position)

        # Calculate the score of children
        movements = rules.possible_movements(position)
        scores = []
        for move in movements:

            next_position = rules.next_position(move, position)
            next_score = self.minimax(next_position, depth - 1, alpha, beta)
            scores.append(next_score)

            if self.player == position.next_player(): # Max player
                alpha = max(alpha, next_score)
            else:
                beta = min(beta, next_score)

            if alpha >= beta:
                break


        # Calculate the score of the position
        final_score = self.select_score(self.player == position.next_player(), scores)

        # Store the score in the cache
        self.cache_store(position, depth, final_score)

        return final_score



class MinimaxCachePlayer(MinimaxPrunePlayer):

    def __init__(
            self,
            player: PlayerIndex = None,
            depth: int = -1,
            alpha: MinimaxScoreType = float('-inf'),
            beta: MinimaxScoreType = float('inf')):
        super().__init__(player, depth, alpha, beta)
        self.cache = []

    @override
    def starting_game(
            self,
            rules: IGameRules,
            player_index: int):
        super().starting_game(rules, player_index)

        # Create enough cache for this player index in case it is not already created
        while len(self.cache) <= player_index:
            self.cache.append({})

    @override
    def cache_store(self, position: IPosition, depth: int, score: MinimaxScoreType):
        # This assumes cache store will never be called if the value is already in the cache
        self.cache[self.player][position] = (depth, score)

    @override
    def cache_get(self, position: IPosition, depth: int) -> MinimaxScoreType:
        if position in self.cache[self.player]:
            d, s = self.cache[self.player][position]
            if d >= depth:
                return s
        return None



class MinimaxRandomConsistentPlayer(MinimaxCachePlayer):

    def __init__(
            self,
            player: PlayerIndex = None,
            depth: int = -1,
            alpha: MinimaxScoreType = float('-inf'),
            beta: MinimaxScoreType = float('inf'),
            seed: int = 0):
        super().__init__(player, depth, alpha, beta)
        self.rg = RandomGenerator(seed)

    @override
    def select_move(self, movements, scores):

        # get best score achievable
        best_score = max(scores)
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


# Alias
StrongestPlayer = MinimaxRandomConsistentPlayer
