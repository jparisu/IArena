from typing import List

from IArena.interfaces.IPlayer import IPlayer
from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.interfaces.ScoreBoard import ScoreBoard
from IArena.interfaces.IMovement import IMovement
from IArena.utils.decorators import override
from IArena.utils.time_limit_run import time_limit_run
from IArena.players.playable_players import PlayablePlayer

class GenericGame:

    def __init__(
                self,
                rules: IGameRules,
                players: List[IPlayer],
                check_correct_move: bool = True,
                max_moves: int = None
            ):

        # If the number of players is not correct, throw exception
        if rules.n_players() != len(players):
            raise ValueError(f'This game requires {rules.n_players()} players.'
                             f'{len(players)} were given.')

        self.rules = rules
        self.players = players
        self.check_correct_move = check_correct_move
        self.max_moves = max_moves


    def play(self) -> ScoreBoard:

        # Initialize the players in the game
        for i, player in enumerate(self.players):
            player.starting_game(self.rules, i)

        current_position = self.rules.first_position()
        finished = self.rules.finished(current_position)
        moves = 0

        while not finished:

            current_position = self.next_movement_(current_position)
            finished = self.rules.finished(current_position)
            moves += 1

            if self.max_moves is not None and moves >= self.max_moves:
                raise TimeoutError(f'Game has exceeded the maximum number of moves: {self.max_moves}.')

        return self.calculate_score_(current_position)


    def next_movement_(self, current_position: IPosition) -> IPosition:
        movement = self.next_player_move_(current_position)

        # Check if the movement is possible
        if not self.rules.is_movement_possible(movement, current_position):
            raise ValueError(f'Player <{self.get_player_name(current_position.next_player())}> has made an invalid movement: {movement} in position:\n{current_position}')

        return self.rules.next_position(
            movement,
            current_position)

    def next_player_move_(self, current_position: IPosition) -> IMovement:
        next_player = current_position.next_player()
        return self.players[next_player].play(current_position)

    def calculate_score_(self, position: IPosition) -> ScoreBoard:
        return self.rules.score(position)

    def get_player_name(self, player_index: PlayerIndex) -> str:
        return f'{self.players[player_index].name()}[{player_index}]'



class BroadcastGame(GenericGame):

    @override
    def next_movement_(self, current_position: IPosition) -> IPosition:
        next_player_index = current_position.next_player()
        movement = self.players[next_player_index].play(current_position)

        # Check if the movement is possible
        # if not self.rules.is_movement_possible(movement, current_position):
        #     raise ValueError(f'Player <{self.get_player_name(next_player_index)}> has made an invalid movement: {movement} in position:\n{current_position}')

        next_position = self.rules.next_position(
            movement,
            current_position)

        print(f'Player <{self.get_player_name(next_player_index)}>  move: <{movement}> ->\n{next_position}')

        return next_position


class ClockGame(GenericGame):

    def __init__(
                self,
                rules: IGameRules,
                players: List[IPlayer],
                move_timeout_s: float = 10.0,
                total_timeout_s: float = float('inf'),
                max_moves: int = None,
            ):
        super().__init__(rules, players, max_moves=max_moves)

        self.move_timeout_s = move_timeout_s
        self.total_timeout_s = total_timeout_s


    def play(self) -> ScoreBoard:

        # Run such function in a new thread that shuts down after move_timeout_s
        try:
            score = time_limit_run(
                self.total_timeout_s,
                super().play)
            return score

        except TimeoutError:
            raise TimeoutError(f'Game has exceeded the total time limit of {self.total_timeout_s} seconds.')



    @override
    def next_player_move_(self, current_position: IPosition) -> IMovement:

        next_player_index = current_position.next_player()

        # Run such function in a new thread that shuts down after move_timeout_s
        try:
            move = time_limit_run(
                self.move_timeout_s,
                self.players[next_player_index].play,
                current_position)
            return move

        except TimeoutError:
            raise TimeoutError(f'Player <{self.get_player_name(next_player_index)}> has exceeded the time limit of {self.move_timeout_s} seconds in position:\n{current_position}')



class PlayableGame(GenericGame):

    def __init__(
            self,
            rules: IGameRules):
        super().__init__(
            rules=rules,
            players=[
                PlayablePlayer() for i in range(rules.n_players())])

    def play(self) -> ScoreBoard:
        score = super().play()
        print(f'SCORE: {score}')
        print(f'WINNER: Player <{score.winner()}>')
        return score
