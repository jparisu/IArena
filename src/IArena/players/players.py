
import random

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IPlayer import IPlayer
from IArena.utils.decorators import override


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


class PlayablePlayer(IPlayer):

    SeparatorN = 40

    @override
    def play(
            self,
            position: IPosition) -> IMovement:

        possibilities = list(position.get_rules().possible_movements(position))

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
