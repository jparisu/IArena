
from typing import Iterator, List

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.interfaces.ScoreBoard import ScoreBoard
from IArena.utils.decorators import override
from IArena.utils.SquareMap import SquareMapCoordinate, SquareMapMovement, SquareMap

"""
This game represents a grid search where some squares represent obstacles/walls.
The target is to reach the destination in the minimum number of moves.
The grid is not known a priori, and must be discovered by the player step by step.
The player can move in 4 directions: up, down, left and right. There is not grid boundary.
The player does not know the position of the origin or destination, it only knows the direction of the destination as a compass.
"""

CompassBlindWalkMovement = SquareMapMovement
CompassBlindWalkCoordinate = SquareMapCoordinate
CompassBlindWalkMap = SquareMap

class CompassBlindWalkPosition(IPosition):
    """
    Represents the position of the player in the grid.

    Attributes:
        rules: IGameRules - The rules of the game.
        steps: int - The number of steps taken to reach this position.
        position: CompassBlindWalkCoordinate - The coordinates of the current position.
        target: CompassBlindWalkCoordinate - The coordinates of the target position.
    """

    def __init__(
            self,
            rules: "CompassBlindWalkRules",
            steps: int,
            position: CompassBlindWalkCoordinate):
        self.rules_ = rules
        self.steps_ = steps
        self.__position = position

    @override
    def next_player(
            self) -> PlayerIndex:
        return PlayerIndex.FirstPlayer

    @override
    def get_rules(self) -> "CompassBlindWalkRules":
        """Get the rules of the game."""
        return self.rules_

    def __eq__(
            self,
            other: "CompassBlindWalkPosition"):
        return self.steps_ == other.steps and self.__position == other.position

    def __str__(self):
        st = f"""Steps: {self.steps_},
        Compass: {self.compass()},
        Free Moves: {' ; '.join([str(x) for x in self.valid_moves()])}"""
        return st

    def cost(self) -> int:
        return self.steps_

    def valid_moves(self) -> List[CompassBlindWalkMovement]:
        return self.rules_.possible_movements(self)

    def compass(self) -> CompassBlindWalkMovement.Direction:
        dx = self.rules_.target_.x - self.__position.x
        dy = self.rules_.target_.y - self.__position.y
        if abs(dx) > abs(dy):
            return CompassBlindWalkMovement.Direction.Down if dx > 0 else CompassBlindWalkMovement.Direction.Up
        else:
            return CompassBlindWalkMovement.Direction.Right if dy > 0 else CompassBlindWalkMovement.Direction.Left

    def _is_goal(self) -> bool:
        return self.rules_.target_ == self.__position

    def _following_coordinate(
            self,
            movement: CompassBlindWalkMovement) -> CompassBlindWalkCoordinate:
        if movement.direction == CompassBlindWalkMovement.Direction.Up:
            return CompassBlindWalkCoordinate(self.__position.x - 1, self.__position.y)
        if movement.direction == CompassBlindWalkMovement.Direction.Down:
            return CompassBlindWalkCoordinate(self.__position.x + 1, self.__position.y)
        if movement.direction == CompassBlindWalkMovement.Direction.Left:
            return CompassBlindWalkCoordinate(self.__position.x, self.__position.y - 1)
        if movement.direction == CompassBlindWalkMovement.Direction.Right:
            return CompassBlindWalkCoordinate(self.__position.x, self.__position.y + 1)
        raise ValueError(f"Invalid movement {movement}")


class CompassBlindWalkRules(IGameRules):

    def __init__(
            self,
            map: CompassBlindWalkMap,
            target: CompassBlindWalkCoordinate,
            start: CompassBlindWalkCoordinate = CompassBlindWalkCoordinate(0, 0)):
        self.__map = map
        self.target_ = target
        self.start_ = start

    @override
    def n_players(self) -> int:
        return 1

    @override
    def first_position(self) -> CompassBlindWalkPosition:
        return CompassBlindWalkPosition(self, 0, self.start_)

    @override
    def next_position(
            self,
            movement: IMovement,
            position: CompassBlindWalkPosition) -> CompassBlindWalkPosition:

        next_coordinate = position._following_coordinate(movement)

        # Check movement is valid
        if not self.is_valid_coordinate(next_coordinate):
            raise ValueError(f"Invalid movement {movement} from position {position}")

        return CompassBlindWalkPosition(
            rules=self,
            steps=position.steps_ + 1,
            position=next_coordinate)


    @override
    def possible_movements(
            self,
            position: CompassBlindWalkPosition) -> Iterator[IMovement]:
        movements = []
        for movement in [CompassBlindWalkMovement.up(), CompassBlindWalkMovement.down(), CompassBlindWalkMovement.left(), CompassBlindWalkMovement.right()]:
            next_coordinate = position._following_coordinate(movement)
            if self.is_valid_coordinate(next_coordinate):
                movements.append(movement)
        return movements


    @override
    def finished(
            self,
            position: CompassBlindWalkPosition) -> bool:
        return position._is_goal()


    @override
    def score(
            self,
            position: CompassBlindWalkPosition) -> ScoreBoard:
        sb = ScoreBoard()
        sb.define_score(PlayerIndex.FirstPlayer, -position.steps_)
        return sb


    def is_valid_coordinate(
            self,
            coordinate: CompassBlindWalkCoordinate) -> bool:
        rows, cols = self.__map.size()
        return (0 <= coordinate.x < rows and
                0 <= coordinate.y < cols and
                self.__map[coordinate.x, coordinate.y])
