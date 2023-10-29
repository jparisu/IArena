
from typing import Dict, Iterator
from enum import Enum
import random

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex, two_player_game_change_player
from IArena.utils.decorators import override
from IArena.interfaces.Score import ScoreBoard

"""
This game represents the Prisoner Dilemma game theory problem.
Given 2 players, can decide whether to cooperate or Defect.
A score table will be given a priori with the score of each player depending on the decision of both.
The goal is to minimize the score of the player.
"""


class PrisonerDilemmaMovement(IMovement):
    """
    Represents the movement of one of the players.

    Values:
        Cooperate: 0 - Cooperate.
        Defect: 1 - Defect.
    """
    Cooperate = 0
    Defect = 1

    def __init__(
            self,
            decision: int):
        self.decision = decision

        if decision != 0:
            self.decision = PrisonerDilemmaMovement.Defect

    def __eq__(
            self,
            other: "PrisonerDilemmaMovement"):
        return self.decision == other.decision

    def __str__(self):
        if self.decision == PrisonerDilemmaMovement.Cooperate:
            return "<Cooperate>"
        else:
            return "<Defect>"

    def cooperate() -> int:
        return PrisonerDilemmaMovement.Cooperate

    def defect() -> int:
        return PrisonerDilemmaMovement.Defect

    def is_cooperate(self) -> bool:
        return self.decision == PrisonerDilemmaMovement.Cooperate

    def is_defect(self) -> bool:
        return self.decision == PrisonerDilemmaMovement.Defect


class PrisonerDilemmaScoreTable:

    def __init__(self, score_table: Dict[PrisonerDilemmaMovement, Dict[PrisonerDilemmaMovement, float]]):
        self.score_table = score_table

    def __str__(self):
        return str(self.score_table)

    def generate_random_table(seed: int = None) -> "PrisonerDilemmaScoreTable":

        if seed is not None:
            random.seed(seed)

        scores = sorted([random.random() for _ in range(4)])
        return PrisonerDilemmaScoreTable({
            PrisonerDilemmaMovement.Cooperate: {
                PrisonerDilemmaMovement.Cooperate: scores[1],
                PrisonerDilemmaMovement.Defect: scores[3]
            },
            PrisonerDilemmaMovement.Defect: {
                PrisonerDilemmaMovement.Cooperate: scores[0],
                PrisonerDilemmaMovement.Defect: scores[2]
            }
        })

    def score(self, player_movement: PrisonerDilemmaMovement, opponent_movement: PrisonerDilemmaMovement) -> float:
        return self.score_table[player_movement.decision][opponent_movement.decision]


class PrisonerDilemmaPosition(IPosition):
    """
    Represents the position of the game by counting the coins remaining.
    This holds in secret the movement of the players until the score() method is called.
    If such method is called before the game is over, it will not return the score.
    """
    def __init__(
            self,
            rules: "PrisonerDilemmaRules",
            last_position: "PrisonerDilemmaPosition" = None,
            new_movement: PrisonerDilemmaMovement = None):
        super().__init__(rules)
        if last_position is None:
            self.__first_player_movement = None
            self.__second_player_movement = None
        elif last_position.first_player_already_played():
            self.__first_player_movement = last_position.__first_player_movement
            self.__second_player_movement = new_movement
        else:
            self.__first_player_movement = new_movement
            self.__second_player_movement = None

    def first_player_already_played(self) -> bool:
        return self.__first_player_movement is not None

    def second_player_already_played(self) -> bool:
        return self.__second_player_movement is not None

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
        return self.__first_player_movement == other.__first_player_movement and self.__second_player_movement == other.__second_player_movement

    def __str__(self):
        return f"Player: {self.next_player()}\nScore Table: {self.rules.get_score_table()}\n"

    def score(self, score_table: PrisonerDilemmaScoreTable) -> dict[PlayerIndex, float]:
        if self.__first_player_movement is None or self.__second_player_movement is None:
            return None

        return {
            PlayerIndex.FirstPlayer: score_table.score(self.__first_player_movement, self.__second_player_movement),
            two_player_game_change_player(PlayerIndex.FirstPlayer): score_table.score(self.__second_player_movement, self.__first_player_movement)
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
            seed: int = None):
        """
        Args:
            initial_position: The number of PrisonerDilemma at the beginning of the game.
            min_play: The minimum number of PrisonerDilemma that can be removed.
            max_play: The maximum number of PrisonerDilemma that can be removed.
        """
        if score_table is None:
            self.score_table = PrisonerDilemmaScoreTable.generate_random_table(seed)
        else:
            self.score_table = score_table

    def get_score_table(self) -> PrisonerDilemmaScoreTable:
        return self.score_table

    @override
    def n_players(self) -> int:
        return 2

    @override
    def first_position(self) -> PrisonerDilemmaPosition:
        return PrisonerDilemmaPosition(rules=self)

    @override
    def next_position(
            self,
            movement: PrisonerDilemmaMovement,
            position: PrisonerDilemmaPosition) -> PrisonerDilemmaPosition:
        return PrisonerDilemmaPosition(
            rules=self,
            last_position=position,
            new_movement=movement)

    @override
    def possible_movements(
            self,
            position: PrisonerDilemmaPosition) -> Iterator[PrisonerDilemmaMovement]:
        return [
            PrisonerDilemmaMovement(PrisonerDilemmaMovement.Cooperate),
            PrisonerDilemmaMovement(PrisonerDilemmaMovement.Defect)
        ]

    @override
    def finished(
            self,
            position: PrisonerDilemmaPosition) -> bool:
        return position.first_player_already_played() and position.second_player_already_played()

    @override
    def score(
            self,
            position: PrisonerDilemmaPosition) -> ScoreBoard:
        scores = position.score(self.score_table)
        s = ScoreBoard()
        s.add_score(PlayerIndex.FirstPlayer, scores[PlayerIndex.FirstPlayer])
        s.add_score(PlayerIndex.SecondPlayer, scores[PlayerIndex.SecondPlayer])

        return s
