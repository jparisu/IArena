
from typing import Iterator

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.ScoreBoard import ScoreBoard
from IArena.utils.decorators import pure_virtual


class IGameRules:
    """
    This abstract class represents the rules of a game.
    """

    @pure_virtual
    def n_players(self) -> int:
        pass

    @pure_virtual
    def first_position(self) -> IPosition:
        pass

    @pure_virtual
    def next_position(
            self,
            movement: IMovement,
            position: IPosition) -> IPosition:
        pass

    @pure_virtual
    def possible_movements(
            self,
            position: IPosition) -> Iterator[IMovement]:
        pass

    @pure_virtual
    def finished(
            self,
            position: IPosition) -> bool:
        pass

    @pure_virtual
    def score(
            self,
            position: IPosition) -> ScoreBoard:
        pass

    def is_movement_possible(
            self,
            movement: IMovement,
            position: IPosition):
        return movement in self.possible_movements(position)
