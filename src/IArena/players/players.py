
import random
# from typing import override

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.interfaces.IPlayer import IPlayer
from IArena.utils.decorators import override

class DummyPlayer(IPlayer):

    def __init__(
            self,
            rules: IGameRules,
            player_index: PlayerIndex):
        self.rules_ = rules
        self.player_index_ = player_index


class FirstPlayer(DummyPlayer):

    @override
    def play(
            self,
            position: IPosition) -> IMovement:
        return self.rules_.possible_movements(position)[0]


class LastPlayer(DummyPlayer):

    @override
    def play(
            self,
            position: IPosition) -> IMovement:
        return self.rules_.possible_movements(position)[-1]


class RandomPlayer(DummyPlayer):

    @override
    def play(
            self,
            position: IPosition) -> IMovement:
        return random.choice(self.rules_.possible_movements(position))


class PlayablePlayer(DummyPlayer):

    SeparatorN = 40

    @override
    def play(
            self,
            position: IPosition) -> IMovement:

        possibilities = list(self.rules_.possible_movements(position))

        print ("=" * PlayablePlayer.SeparatorN)
        print (f"Next player: {position.next_player()}")
        print ("-" * PlayablePlayer.SeparatorN)
        print (position)
        print ("-" * PlayablePlayer.SeparatorN)
        print ("Movements:")

        for i, p in enumerate(possibilities):
            print(f' {i}: {p}')

        print ("=" * PlayablePlayer.SeparatorN)

        move = int(input())

        return possibilities[move]


class RecordPlayer(IPlayer):

    def __init__(
            self,
            player: IPlayer):
        self.player = player
        self.movements = []


    @override
    def play(
            self,
            position: IPosition) -> IMovement:
        move = self.player.play(position)
        self.movements.append(move)
        return move
