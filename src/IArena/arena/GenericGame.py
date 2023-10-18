from typing import List

from IArena.interfaces.IPlayer import IPlayer
from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.interfaces.Score import ScoreBoard
from IArena.interfaces.IMovement import IMovement
from IArena.utils.decorators import override

class GenericGame:

    def __init__(
            self,
            rules: IGameRules,
            players: List[IPlayer]):

        # If the number of players is not correct, throw exception
        if rules.n_players() != len(players):
            raise ValueError(f'This game requires {rules.n_players()} players.'
                             f'{len(players)} were given.')

        self.rules = rules
        self.players = players


    def play(self) -> ScoreBoard:
        current_position = self.rules.first_position()
        finished = self.rules.finished(current_position)
        while not finished:
            current_position = self.next_movement_(current_position)
            finished = self.rules.finished(current_position)
        return self.calculate_score_(current_position)


    def next_movement_(self, current_position: IPosition) -> IPosition:
        movement = self.next_player_move_(current_position)

        # Check if the movement is possible
        if not self.rules.is_movement_possible(movement, current_position):
            raise ValueError(f'Invalid movement: {movement}')

        return self.rules.next_position(
            movement,
            current_position)

    def next_player_move_(self, current_position: IPosition) -> IMovement:
        next_player = current_position.next_player()
        return self.players[next_player].play(current_position)

    def calculate_score_(self, position: IPosition) -> PlayerIndex:
        return self.rules.score(position)


class BroadcastGame(GenericGame):

    @override
    def next_movement_(self, current_position: IPosition) -> IPosition:
        next_player = current_position.next_player()
        movement = self.players[next_player].play(current_position)

        # Check if the movement is possible
        if not self.rules.is_movement_possible(movement, current_position):
            raise ValueError(f'Invalid movement: {movement}')

        next_position = self.rules.next_position(
            movement,
            current_position)

        print(f'Player <{next_player}>  move: <{movement}> ->\n {next_position}')

        return next_position
