
from typing import Dict, Iterator, List

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex, two_player_game_change_player
from IArena.utils.decorators import override

"""
This game represents the Prisioner Dilemma game.
2 players must decide whether collaborate or not in a series of decisions.
The game is focused to increase score, and not to beat the opponent.
"""

class PrisonerDilemmaMovement(IMovement):
    """

    """

    def __init__(
            self,
            decision: bool):
        self.decision = decision

    def __eq__(
            self,
            other: "PrisonerDilemmaMovement"):
        return self.decision == other.decision

    def __str__(self):
        return f'{{remove: {self.decision}}}'


class PrisonerDilemmaPosition(IPosition):
    """
    Represents the position of the game by counting the PrisonerDilemma remaining.

    Attributes:
        n: The number of PrisonerDilemma still in play.
    """

    def __init__(
            self,
            scores: Dict[PlayerIndex, float],
            decisions: Dict[PlayerIndex, List[PrisonerDilemmaMovement]],
            last_decision: PrisonerDilemmaMovement = None):
        self.scores = scores
        self.decisions = decisions
        self.__last_decisions = last_decision

    @override
    def next_player(
            self) -> PlayerIndex:
        # Assuming players are 0 and 1, this converts 1 to 0 and viceversa
        return self.next_player_

    def __eq__(
            self,
            other: "PrisonerDilemmaPosition"):
        return self.n == other.n and self.next_player_ == other.next_player_

    def __str__(self):
        st = "----------------\n"
        st += f"Player: {self.next_player_}\n"
        for i in range(self.n):
            st += (" {0:3d}   === \n".format(i))
        st += "----------------\n"
        return st


class PrisonerDilemmaRules(IGameRules):

    def __init__(
            self,
            initial_position: int = 15,
            min_play: int = 1,
            max_play: int = 3):
        """
        Args:
            initial_position: The number of PrisonerDilemma at the beginning of the game.
            min_play: The minimum number of PrisonerDilemma that can be removed.
            max_play: The maximum number of PrisonerDilemma that can be removed.
        """
        self.initial_position = initial_position
        self.min_play = min_play
        self.max_play = max_play

    @override
    def n_players(self) -> int:
        return 2

    @override
    def first_position(self) -> PrisonerDilemmaPosition:
        return PrisonerDilemmaPosition(
            self.initial_position,
            PlayerIndex.FirstPlayer)

    @override
    def next_position(
            self,
            movement: PrisonerDilemmaMovement,
            position: PrisonerDilemmaPosition) -> PrisonerDilemmaPosition:
        return PrisonerDilemmaPosition(
            position.n - movement.n,
            two_player_game_change_player(position.next_player))

    @override
    def possible_movements(
            self,
            position: PrisonerDilemmaPosition) -> Iterator[PrisonerDilemmaMovement]:
        return [
            PrisonerDilemmaMovement(x) for x in range(
                self.min_play,
                min(
                    position.n,
                    self.max_play
                ) + 1
            )
        ]

    @override
    def finished(
            self,
            position: PrisonerDilemmaPosition) -> bool:
        return position.n < self.min_play

    @override
    def score(
            self,
            position: PrisonerDilemmaPosition) -> dict[PlayerIndex, float]:
        return {
            position.next_player() : 0.0,
            two_player_game_change_player(position.next_player()) : 1.0
        }
