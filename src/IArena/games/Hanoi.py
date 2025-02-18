
from typing import Iterator, List
from queue import LifoQueue

from IArena.interfaces.IPosition import CostPosition, CostType
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex, two_player_game_change_player
from IArena.interfaces.ScoreBoard import ScoreBoard
from IArena.utils.decorators import override

"""
This game represents the Hanoi Tower game.
There are N towers and M pieces numerated from 1 to M.
In each turn, the player can move one piece from one tower to another.
There cannot be a bigger piece on top of a smaller piece.
The end games when all the pieces are in the last tower.

NOTE: Bigger pieces are the one with lower index.
"""

class HanoiPosition(CostPosition):
    """
    Represents the position of the game with the pieces in each tower.

    Attributes:
        towers: List[List[int]]: The pieces in each tower.
        movements: The number of movements made so far.

    NOTE: Bigger pieces are the one with lower index.
    """

    def __init__(
            self,
            rules: "IGameRules",
            towers: List[List[int]],
            cost: CostType):
        super().__init__(rules, cost)
        self.towers = towers

    @override
    def next_player(
            self) -> PlayerIndex:
        return PlayerIndex.FirstPlayer

    def __eq__(
            self,
            other: "HanoiPosition"):
        return self.towers == other.towers and self.cost() == other.cost()

    def __str__(self):

        max_height = max([len(tower) for tower in self.towers])
        max_piece = max([max(tower, default=0) for tower in self.towers])+1
        max_width = max_piece * 2

        st = ""
        st += f"Cost: {self.cost()}\n\n"

        for level in reversed(range(max_height)):
            for tower in self.towers:
                if level < len(tower):
                    piece_width = (max_piece - tower[level]) * 2
                    padding = (max_width - piece_width) // 2
                    st += " " * padding + "#" * piece_width + " " * padding + " "
                else:
                    st += " " * max_width + " "
            st += "\n"

        for i, _ in enumerate(self.towers):
            st += "=" * max_width + " "

        st += "\n"

        return st


class HanoiMovement(IMovement):
    """
    Represents the movement of the player in the game by moving a piece from the top of one tower to another.

    Attributes:
        tower_source: The tower from where the piece is removed.
        tower_target: The tower to where the piece is moved.
    """

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

    DefaultPieces = 4

    @staticmethod
    def generate_initial_towers(n: int) -> List[List[int]]:
        return [list(range(n)), [], []]

    def __init__(
            self,
            n: int = DefaultPieces):
        """
        Args:
            n: The number of pieces in the game.
        """
        self.n = n

    @override
    def n_players(self) -> int:
        return 1

    @override
    def first_position(self) -> HanoiPosition:
        return HanoiPosition(
            rules=self,
            towers=HanoiRules.generate_initial_towers(self.n),
            cost=0)

    @override
    def next_position(
            self,
            movement: HanoiMovement,
            position: HanoiPosition) -> HanoiPosition:

        new_position = HanoiPosition(
            rules=self,
            towers=position.towers.copy(),
            cost=position.cost() + 1)

        x = new_position.towers[movement.tower_source].pop()
        new_position.towers[movement.tower_target].append(x)

        return new_position

    @override
    def possible_movements(
            self,
            position: HanoiPosition) -> Iterator[HanoiMovement]:
        movements_result = []
        top_towers = [tower[-1] if len(tower) > 0 else -1 for tower in position.towers]

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
            position: HanoiPosition) -> ScoreBoard:
        s = ScoreBoard()
        s.add_score(PlayerIndex.FirstPlayer, position.cost())
        return s
