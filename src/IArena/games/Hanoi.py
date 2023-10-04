
from typing import Iterator, List
from queue import LifoQueue

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex, two_player_game_change_player
from IArena.utils.decorators import override

"""
This game represents the Hanoi Tower game.
There are N towers and M pieces numerated from 1 to M.
In each turn, the player can move one piece from one tower to another.
There cannot be a bigger piece on top of a smaller piece.
The end games when all the pieces are in the last tower.

NOTE: Bigger pieces are the one with lower index.
"""

class HanoiPosition(IPosition):

    def __init__(
            self,
            towers: List[List[int]],
            movements: int):
        self.towers = towers
        self.movements = movements

    @override
    def next_player(
            self) -> PlayerIndex:
        return PlayerIndex.FirstPlayer

    def __eq__(
            self,
            other: "HanoiPosition"):
        return self.towers == other.towers and self.movements == other.movements

    def __str__(self):

        max_height = max([len(tower) for tower in self.towers])
        max_piece = max([max(tower, default=0) for tower in self.towers])
        max_width = max_piece * 2

        st = ""
        st += "\n" + "=" * (max_width + 1) * len(self.towers) + "\n"
        st += f"Movements: {self.movements}\n\n"

        for level in reversed(range(max_height)):
            for tower in self.towers:
                if level < len(tower):
                    piece_width = (max_piece - tower[level] + 1) * 2
                    padding = (max_width - piece_width) // 2
                    st += " " * padding + "#" * piece_width + " " * padding + " "
                else:
                    st += " " * max_width + " "
            st += "\n"

        for i, _ in enumerate(self.towers):
            st += "=" * max_width + " "
        st += "\n" + "=" * (max_width + 1) * len(self.towers) + "\n"
        st += "\n"

        return st


class HanoiMovement(IMovement):

    def __init__(
            self,
            tower_source: int,
            tower_target: int):
        self.tower_source = tower_source
        self.tower_target = tower_target

    def __eq__(
            self,
            other: "HanoiMovement"):
        return self.tower_source == other.tower_source and self.tower_target == other.tower_target

    def __str__(self):
        return f'{{from: {self.tower_source}  to: {self.tower_target}}}'


class HanoiRules(IGameRules):

    def __init__(
            self,
            initial_towers: List[List[int]] = [[1, 2, 3, 4], [], []]):
        self.initial_towers = initial_towers

    @override
    def n_players(self) -> int:
        return 1

    @override
    def first_position(self) -> HanoiPosition:
        return HanoiPosition(
            towers=self.initial_towers,
            movements=0)

    @override
    def next_position(
            self,
            movement: HanoiMovement,
            position: HanoiPosition) -> HanoiPosition:

        new_position = HanoiPosition(
            towers=position.towers.copy(),
            movements=position.movements + 1)

        x = new_position.towers[movement.tower_source].pop()
        new_position.towers[movement.tower_target].append(x)

        return new_position

    @override
    def possible_movements(
            self,
            position: HanoiPosition) -> Iterator[HanoiMovement]:
        movements_result = []
        top_towers = [tower[-1] if len(tower) > 0 else 0 for tower in position.towers]

        for i in range(len(position.towers)):
            for j in range(len(position.towers)):
                if i != j and (top_towers[i] > top_towers[j]):
                    movements_result.append(HanoiMovement(i, j))

        return movements_result

    @override
    def finished(
            self,
            position: HanoiPosition) -> bool:
        # The game is finished when all the elements are in the last tower
        # Thus, when all towers except last are empty
        for tower in position.towers[:-1]:
            if len(tower) > 0:
                return False
        return True


    @override
    def score(
            self,
            position: HanoiPosition) -> dict[PlayerIndex, float]:
        return {PlayerIndex.FirstPlayer : position.movements}
