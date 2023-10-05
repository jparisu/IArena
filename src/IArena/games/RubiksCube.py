
from typing import Dict, Iterator
import numpy as np
import random

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex, two_player_game_change_player
from IArena.utils.decorators import override

"""
This game represents the RubiksCube game of NxNxN.
In a 6 face cube, all faces must have only one color.

+-----+
|·    |
| C4  |
|     |
+-----+-----+-----+-----+
|·    |·    |·    |·    |
| C0  | C1  | C2  | C3  |
|     |     |     |     |
+-----+-----+-----+-----+
|·    |
| C5  |
|     |
+-----+

"""

class RubiksCubeMovement(IMovement):

    def __init__(
            self,
            face: int,
            clockwise: bool = True):
        self.face = face
        self.clockwise = clockwise

    def __eq__(
            self,
            other: "RubiksCubeMovement"):
        return self.face == other.face and self.clockwise == other.clockwise

    def __str__(self):
        return f'{{face: {self.face}  clockwise: {self.clockwise}}}'


class RubiksCubePosition(IPosition):

    def __init__(
            self,
            faces: Dict[int, np.matrix],
            cost: int):
        self.faces = faces
        self.cost = cost

    @override
    def next_player(
            self) -> PlayerIndex:
        return PlayerIndex.FirstPlayer

    def __eq__(
            self,
            other: "RubiksCubePosition"):
        return self.faces == other.faces and self.cost == other.cost

    def __str__(self):
        st = "----------------\n"
        st += f"{self.faces}  <{self.cost}>\n"
        st += "----------------\n"
        return st

    def random_generator(n: int, seed: int):
        random.seed(seed)

        faces = {}
        for i in range(6):
            faces[i] = np.full((n, n), i)

        position = RubiksCubePosition(faces, 0)

        for i in range(100):
            face = random.randint(0, 5)
            clockwise = random.choice(True, False)
            position = RubiksCubeRules.next_position(position, RubiksCubeMovement(face, clockwise))

        return RubiksCubePosition(position.faces, 0)


class RubiksCubeRules(IGameRules):

    def __init__(
            self,
            initial_position: RubiksCubePosition = None,
            size: int = 2,
            seed: int = 0):
        if initial_position:
            self.initial_position = initial_position
        else:
            self.initial_position = RubiksCubePosition.random_generator(
                size, seed)

    @override
    def n_players(self) -> int:
        return 1

    @override
    def first_position(self) -> RubiksCubePosition:
        return self.initial_position

    @override
    def next_position(
            self,
            movement: RubiksCubeMovement,
            position: RubiksCubePosition) -> RubiksCubePosition:
        # If movement is not clokwise, we can do 3 clockwise movements and then rest 2 to cost
        if not movement.clockwise:
            next_position = position
            for i in range(3):
                next_position = self.next_position(RubiksCubeMovement(movement.face, True), next_position)
            return RubiksCubePosition(next_position.faces, next_position.cost-2)

        # Clockwise movement
        faces = position.faces.copy()

        if movement.face == 0:
            # Clockwise movement of face 0
            faces[0] = np.rot90(faces[0], 3)

            # Change of faces 1, 4, 3, 5
            faces_1_rotated = faces[1][:, 0]
            faces[1][:, 0] = faces[4][1, :]
            faces[4][1, :] = faces[3][:, 1].transpose()
            faces[3][:, 0] = faces[5][:, 0]
            faces[5][:, 0] = faces_1_rotated

        elif movement.face == 1:
            # Clockwise movement of face 0
            faces[1] = np.rot90(faces[0], 3)

            # Change of faces 2, 4, 0, 5
            faces_2_rotated_0 = faces[2][0, 0]
            faces_2_rotated_1 = faces[2][0, 1]
            faces[4][1, 0] = faces[3][1, 1]
            faces[4][1, 1] = faces[3][0, 1]
            faces[3][1, 1] = faces[2][0, 1]
            faces[3][1, 0] = faces[2][0, 0]
            faces[2][0, 1] = faces[1][1, 0]
            faces[2][0, 0] = faces[1][0, 0]
            faces[1][0, 0] = faces_2_rotated_0
            faces[1][1, 0] = faces_2_rotated_1

"""
+-----+
|·    |
| C4  |
|    *|
+-----+-----+-----+-----+
|·    |·    |·    |·    |
| C0  | C1  | C2  | C3  |
|    *|    *|    *|    *|
+-----+-----+-----+-----+
|·    |
| C5  |
|    *|
+-----+
"""

    @override
    def possible_movements(
            self,
            position: RubiksCubePosition) -> Iterator[RubiksCubeMovement]:
        return [
            RubiksCubeMovement(x, y) for x, y in range(
                zip(range(6), [True, False])
            )
        ]

    @override
    def finished(
            self,
            position: RubiksCubePosition) -> bool:
        for face in position.faces:
            if not np.all(face == face[0,0]):
                return False
        return True

    @override
    def score(
            self,
            position: RubiksCubePosition) -> dict[PlayerIndex, float]:
        return position.cost
