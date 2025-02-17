
import random
import math
from typing import Tuple

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IPlayer import IPlayer
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.utils.decorators import override
from IArena.utils.RandomGenerator import RandomGenerator


class MinimaxHeuristicPlayer(IPlayer):

    MAX_SCORE = 2**31

    def __init__(self, heuristic: callable, depth: int = 1):
        self.player = None
        self.depth = depth
        self.heuristic = heuristic

    @override
    def play(
            self,
            position: IPosition) -> IMovement:

        scores = []
        movements = position.get_rules().possible_movements(position)

        self.player = position.next_player()

        for move in movements:
            next_position = position.get_rules().next_position(move, position)
            scores.append(self._minimax(next_position, self.depth))

        return self._select_move(movements, scores)


    def _minimax(self, position: IPosition, depth: int = -1) -> int:

        rules = position.get_rules()
        if rules.finished(position):
            s = rules.score(position)
            return s.get_score(self.player)

        if depth == 0:
            return self.heuristic(position)

        max_play = self.player == position.next_player()

        f_player = max if max_play else min
        score = -MinimaxHeuristicPlayer.MAX_SCORE if max_play else MinimaxHeuristicPlayer.MAX_SCORE

        for move in rules.possible_movements(position):
            next_position = rules.next_position(move, position)
            next_score = self._minimax(next_position, depth - 1)
            score = f_player(next_score, score)

        return score

    def _select_move(self, movements, scores):
        return movements[scores.index(max(scores))]


class MinimaxCachePlayer(MinimaxPlayer):

    def __init__(self, depth: int = -1, unknown_score: int = 0):
        super().__init__(depth, unknown_score)
        self.cache = {}

    @override
    def _minimax(self, position: IPosition, depth: int = -1) -> int:

        return self.__minimax(position, depth)[0]

    @override
    def __minimax(self, position: IPosition, depth: int = -1) -> Tuple[int, bool]:

        # Check if the game is finished
        rules = position.get_rules()
        if rules.finished(position):
            s = rules.score(position)
            return s.get_score(self.player), True

        # Check if the position is in the cache
        if position in self.cache:
            return self.cache[position], True

        # Whether the current player is this object player
        # This object player is the maximizing player
        max_play = self.player == position.next_player()

        # If no more depth, return unknown score
        if depth == 0:
            if max_play:
                return self.unknown_score, False
            else:
                return -self.unknown_score, False

        # Get max or min function
        f_player = max if max_play else min
        # Initialize score
        score = -MinimaxPlayer.MAX_SCORE if max_play else MinimaxPlayer.MAX_SCORE
        any_final = False
        all_final = True

        # Iterate over possible movements
        for move in rules.possible_movements(position):
            next_position = rules.next_position(move, position)
            next_score, is_final = self.__minimax(next_position, depth - 1)
            if is_final:
                any_final = True
                score = f_player(next_score, score)
            else:
                all_final = False

        # In case we are in highest depth, we store the score
        if depth == self.depth:
            self.cache[position] = score

        if not any_final:
            return self.unknown_score, False
        elif all_final:
            self.cache[position] = score
            return score, True
        else:
            if max_play:
                if score > self.unknown_score:
                    self.cache[position] = score
                    return score, True
                else:
                    return self.unknown_score, False
            else:
                if score < -self.unknown_score:
                    self.cache[position] = score
                    return score, True
                else:
                    return self.unknown_score, False

    def _select_move(self, movements, scores):
        # replace every None with minimum score
        min_score = min([x for x in scores if x is not None])
        scores = [score if score is not None else min_score for score in scores]
        return movements[scores.index(max(scores))]



class MinimaxMemoryPlayer(MinimaxPlayer):

    def __init__(self, depth: int = -1, unknown_score: int = 0):
        super().__init__(depth, unknown_score)
        self.memory = {}

    @override
    def _minimax(self, position: IPosition, depth: int = -1) -> int:
        return self.__minimax(position, depth)

    def get_memory(self, position: IPosition, depth: int) -> Tuple[int, bool]:
        if position in self.memory:
            if self.memory[position][0] >= depth:
                return self.memory[position][1], True
        return None, False

    def set_memory(self, position: IPosition, depth: int, score: int):
        self.memory[position] = (depth, score)

    @override
    def __minimax(self, position: IPosition, depth: int = -1) -> int:

        # Check if the position is in the cache
        mem, found = self.get_memory(position, depth)
        if found:
            return mem

        # Check if the game is finished
        rules = position.get_rules()
        if rules.finished(position):
            s = rules.score(position).get_score(self.player)
            self.set_memory(position, self.depth+1, s)
            return s

        # If no more depth, return unknown score
        if depth == 0:
            return None

        # Whether the current player is this object player
        # This object player is the maximizing player
        max_play = self.player == position.next_player()

        # Get max or min function
        f_player = max if max_play else min
        # Initialize score
        score = -MinimaxPlayer.MAX_SCORE if max_play else MinimaxPlayer.MAX_SCORE
        any_final = False
        all_final = True

        # Iterate over possible movements
        for move in rules.possible_movements(position):
            next_position = rules.next_position(move, position)
            next_score = self.__minimax(next_position, depth - 1)
            if next_score:
                any_final = True
                score = f_player(next_score, score)
            else:
                all_final = False

        if not any_final:
            self.set_memory(position, depth, None)
            return None

        elif all_final:
            self.set_memory(position, self.depth+1, score)
            return score

        else:
            if max_play:
                if score > self.unknown_score:
                    self.set_memory(position, depth, score)
                    return score
                else:
                    self.set_memory(position, depth, None)
                    return None
            else:
                if score < -self.unknown_score:
                    self.set_memory(position, depth, score)
                    return score
                else:
                    return None

    def _select_move(self, movements, scores):
        # replace every None with unknown score
        scores = [score if score is not None else self.unknown_score for score in scores]
        return movements[scores.index(max(scores))]



class MinimaxRandomConsistentPlayer(MinimaxMemoryPlayer):

    def __init__(self, depth: int = -1, seed: int = 0):
        super().__init__(depth)
        self.rg = RandomGenerator(seed)

    @override
    def _select_move(self, movements, scores):

        min_score = self.unknown_score
        if not all(score is None for score in scores):
            min_score = min([x for x in scores if x is not None])

        scores = [score if score is not None else min_score for score in scores]

        # get best score achivable
        best_score = max(scores)
        # get movements with best score
        best_movements = [movements[i] for i, score in enumerate(scores) if score == best_score]
        # select a random one
        move = self.rg.choice(best_movements)

        print(f"Size of memory: {len(self.memory)}")
        print(f"Score: {scores}: for: {' ; '.join(map(str,movements))}")
        print(f"Best score: {best_score}: selecting move: {move}")

        return move
