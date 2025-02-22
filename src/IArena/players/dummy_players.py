
import random
import math

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.IPlayer import IPlayer
from IArena.utils.decorators import override
from IArena.utils.RandomGenerator import RandomGenerator


class FirstPlayer(IPlayer):

    @override
    def play(
            self,
            position: IPosition) -> IMovement:
        return position.get_rules().possible_movements(position)[0]


class LastPlayer(IPlayer):

    @override
    def play(
            self,
            position: IPosition) -> IMovement:
        return position.get_rules().possible_movements(position)[-1]


class RandomPlayer(IPlayer):

    @override
    def play(
            self,
            position: IPosition) -> IMovement:
        return random.choice(position.get_rules().possible_movements(position))


class ConsistentRandomPlayer(IPlayer):

    def __init__(self, seed: int = 0, name: str = None):
        super().__init__(name=name)
        self.initial_seed = seed
        self.rg = RandomGenerator(seed)

    @override
    def play(
            self,
            position: IPosition) -> IMovement:
        movements = position.get_rules().possible_movements(position)
        selection = self.rg.randint(0, len(movements) - 1)
        return movements[selection]


class MatchConsistentRandomPlayer(ConsistentRandomPlayer):

    @override
    def starting_game(
            self,
            rules: IGameRules,
            player_index: int):
        self.rg.reset_seed()
