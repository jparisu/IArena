
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
The player can move in 4 directions: up, down, left and right, without going through walls or outside the grid.
The player knows its initial position, and the destination position as square coordinates.

There is a variation of the game where there are no coordinates, but a compass indicating the direction of the destination.
"""

BlindWalkMovement = SquareMapMovement
BlindWalkCoordinate = SquareMapCoordinate
BlindWalkMap = SquareMap

class BlindWalkPosition(IPosition):
    """
    Represents the position of the player in the grid.

    Attributes:
        rules: IGameRules - The rules of the game.
        steps: int - The number of steps taken to reach this position.
        position: BlindWalkCoordinate - The coordinates of the current position.
        target: BlindWalkCoordinate - The coordinates of the target position.
    """

    def __init__(
            self,
            rules: "IGameRules",
            steps: int,
            position: BlindWalkCoordinate):
        self.rules_ = rules
        self.steps_ = steps
        self.position_ = position

    @override
    def next_player(
            self) -> PlayerIndex:
        return PlayerIndex.FirstPlayer

    @override
    def get_rules(self) -> "IGameRules":
        """Get the rules of the game."""
        return self.rules_

    def __eq__(
            self,
            other: "BlindWalkPosition"):
        return self.steps_ == other.steps and self.position_ == other.position

    def __str__(self):
        return f'Steps: {self.steps_}, Position: {self.position_}'

    def cost(self) -> int:
        return self.steps_

    def valid_neighbors(self) -> List[BlindWalkMovement]:
        return list(self.rules_.possible_movements(self))

    def goal(self) -> BlindWalkCoordinate:
        return self.rules_.target_

    def current_coordinate(self) -> BlindWalkCoordinate:
        return self.position_

    def following_coordinate(
            self,
            movement: BlindWalkMovement) -> BlindWalkCoordinate:
        if movement == BlindWalkMovement.Up:
            return BlindWalkCoordinate(self.position_.x - 1, self.position_.y)
        if movement == BlindWalkMovement.Down:
            return BlindWalkCoordinate(self.position_.x + 1, self.position_.y)
        if movement == BlindWalkMovement.Left:
            return BlindWalkCoordinate(self.position_.x, self.position_.y - 1)
        if movement == BlindWalkMovement.Right:
            return BlindWalkCoordinate(self.position_.x, self.position_.y + 1)
        raise ValueError(f"Invalid movement {movement}")



class BlindWalkRules(IGameRules):

    def __init__(
            self,
            map: BlindWalkMap,
            target: BlindWalkCoordinate,
            start: BlindWalkCoordinate = BlindWalkCoordinate(0, 0)):
        self.map_ = self.map
        self.target_ = target
        self.start_ = start

    @override
    def n_players(self) -> int:
        return 1

    @override
    def first_position(self) -> IPosition:
        return BlindWalkPosition(self, 0, self.start_)

    @override
    def next_position(
            self,
            movement: IMovement,
            position: IPosition) -> IPosition:

        next_coordinate = self.following_coordinate(position.position_, movement)

        # Check movement is valid
        if not self.is_valid_coordinate(next_coordinate):
            raise ValueError(f"Invalid movement {movement} from position {position}")

        return BlindWalkPosition(
            rules=self,
            steps=position.steps_ + 1,
            position=next_coordinate)


    @override
    def possible_movements(
            self,
            position: IPosition) -> Iterator[IMovement]:
        movements = []
        for movement in [BlindWalkMovement.up(), BlindWalkMovement.down(), BlindWalkMovement.left(), BlindWalkMovement.right()]:
            next_coordinate = self.following_coordinate(position.position_, movement)
            if self.is_valid_coordinate(next_coordinate):
                movements.append(movement)
        return movements


    @override
    def finished(
            self,
            position: IPosition) -> bool:
        return position.position_ == self.target_


    @override
    def score(
            self,
            position: IPosition) -> ScoreBoard:
        sb = ScoreBoard()
        sb.define_score(PlayerIndex.FirstPlayer, -position.steps_)
        return sb


    def is_valid_coordinate(
            self,
            coordinate: BlindWalkCoordinate) -> bool:
        rows, cols = self.map_.size()
        return (0 <= coordinate.x < rows and
                0 <= coordinate.y < cols and
                self.map_[coordinate.x][coordinate.y])
