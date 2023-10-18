
from typing import Dict, Iterator
from enum import Enum
import random

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex, two_player_game_change_player
from IArena.utils.decorators import override

"""
This game represents the Prisoner Dilemma game theory problem.
Given 2 players, can decide whether to cooperate or betray.
A score table will be given a priori with the score of each player depending on the decision of both.
The goal is to minimize the score of the player.
"""


class PrisonerDilemmaMovement(Enum, IMovement):
    """
    Represents the movement of one of the players.

    Values:
        Cooperate: 0 - Cooperate.
        Betray: 1 - Betray.
    """
    Cooperate = 0
    Betray = 1


class PrisonerDilemmaScoreTable:

    def __init__(self, score_table: Dict[Dict[PrisonerDilemmaMovement, float]]):
        self.score_table = score_table

    def __str__(self):
        return str(self.score_table)

    def generate_random_table(self, seed: int = 0) -> "PrisonerDilemmaScoreTable":
        random.seed(seed)
        scores = sorted([random.random() for _ in range(4)])
        return {
            PrisonerDilemmaMovement.Cooperate: {
                PrisonerDilemmaMovement.Cooperate: scores[1],
                PrisonerDilemmaMovement.Betray: scores[3]
            },
            PrisonerDilemmaMovement.Betray: {
                PrisonerDilemmaMovement.Cooperate: scores[0],
                PrisonerDilemmaMovement.Betray: scores[2]
            }
        }

    def score(self, player_movement: PrisonerDilemmaMovement, opponent_movement: PrisonerDilemmaMovement) -> float:
        return self.score_table[player_movement][opponent_movement]

class PrisonerDilemmaPosition(IPosition):
    """
    Represents the position of the game by counting the coins remaining.
    This holds in secret the movement of the players until the score() method is called.
    If such method is called before the game is over, it will not return the score.
    """
    def __init__(
            self,
            first_player_position: "PrisonerDilemmaPosition" = None,
            new_movement: PrisonerDilemmaMovement = None):
        if first_player_position:
            self.__first_player_movement = first_player_position.__new_movement
            self.__new_movement = new_movement
        else:
            self.__first_player_movement = new_movement
            self.__new_movement = None

    def first_player_already_played(self) -> bool:
        return self.__first_player_movement is not None

    def second_player_already_played(self) -> bool:
        return self.__new_movement is not None

    @override
    def next_player(
            self) -> PlayerIndex:
        if self.__first_player_movement is None:
            return PlayerIndex.FirstPlayer
        else:
            return two_player_game_change_player(PlayerIndex.FirstPlayer)

    def __eq__(
            self,
            other: "PrisonerDilemmaPosition"):
        return self.__first_player_movement == other.__first_player_movement and self.__new_movement == other.__new_movement

    def __str__(self):
        return f"Player: {self.next_player()}"

    def score(self, score_table: PrisonerDilemmaScoreTable) -> dict[PlayerIndex, float]:
        if self.__first_player_movement is None or self.__new_movement is None:
            return None

        return {
            PlayerIndex.FirstPlayer: score_table.score_table(self.__first_player_movement, self.__new_movement),
            two_player_game_change_player(PlayerIndex.FirstPlayer): score_table.score_table(self.__new_movement, self.__first_player_movement)
        }


class PrisonerDilemmaRules(IGameRules):
    """
    This rules contains the punctuation table of the Prisoner Dilemma game.
    Such score table is a dictionary of dictionaries where the score of each player is calculated by:
    score_table[player_movement][opponent_movement]
    """

    def __init__(
            self,
            score_table: PrisonerDilemmaScoreTable = None,
            seed: int = 0):
        """
        Args:
            initial_position: The number of PrisonerDilemma at the beginning of the game.
            min_play: The minimum number of PrisonerDilemma that can be removed.
            max_play: The maximum number of PrisonerDilemma that can be removed.
        """
        if score_table is None:
            score_table = PrisonerDilemmaScoreTable.generate_random_table(seed)

    @override
    def n_players(self) -> int:
        return 2

    @override
    def first_position(self) -> PrisonerDilemmaPosition:
        return PrisonerDilemmaPosition()

    @override
    def next_position(
            self,
            movement: PrisonerDilemmaMovement,
            position: PrisonerDilemmaPosition) -> PrisonerDilemmaPosition:
        if position.first_player_already_played():
            return PrisonerDilemmaPosition(
                first_player_position=position,
                new_movement=movement)

    @override
    def possible_movements(
            self,
            position: PrisonerDilemmaPosition) -> Iterator[PrisonerDilemmaMovement]:
        return [
            PrisonerDilemmaMovement.Cooperate,
            PrisonerDilemmaMovement.Betray
        ]

    @override
    def finished(
            self,
            position: PrisonerDilemmaPosition) -> bool:
        return position.first_player_already_played() and position.second_player_already_played()

    @override
    def score(
            self,
            position: PrisonerDilemmaPosition) -> dict[PlayerIndex, float]:
        return position.score()
