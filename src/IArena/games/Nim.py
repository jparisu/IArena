
from typing import Iterator, List

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex, two_player_game_change_player
from IArena.utils.decorators import override

"""
This game represents the Nim game.
There are N piles of arbitrary sizes, and two players.
In turns, each player can take as many elements from a pile as they want.
The player that takes the last element loses.
"""

class NimPosition(IPosition):
    """
    Represents the position of the game by counting the stick remaining in each line.

    Attributes:
        lines: List[int] The number of sticks in each line.
    """

    def __init__(
            self,
            lines: List[int],
            next_player: PlayerIndex):
        self.lines = lines
        self.next_player_ = next_player

    @override
    def next_player(
            self) -> PlayerIndex:
        return self.next_player_

    def __eq__(
            self,
            other: "NimPosition"):
        return self.lines == other.lines and self.next_player_ == other.next_player_

    def __str__(self):
        st = "----------------\n"
        st += f"Player: {self.next_player_}\n"
        for i, num in enumerate(self.lines):
            st += (f"  {i}: {'|' * num}\n")
        st += "----------------\n"
        return st


class NimMovement(IMovement):
    """
    Represents the movement of the player in the game by counting the sticks removed from a specific line.

    Attributes:
        line_index: The index of the line from which the sticks are removed.
        remove: The number of sticks to remove.
    """

    def __init__(
            self,
            line_index: int,
            remove: int):
        self.line_index = line_index
        self.remove = remove

    def __eq__(
            self,
            other: "NimMovement"):
        return self.line_index == other.line_index and self.remove == other.remove

    def __str__(self):
        return f'{{line: {self.line_index}   remove: {self.remove}}}'


class NimRules(IGameRules):

    def __init__(
            self,
            original_lines: List[int] = [1, 3, 5, 7]):
        """
        Args:
            original_lines: The initial position of the lines.
        """
        self.original_lines = original_lines

    @override
    def n_players(self) -> int:
        return 2

    @override
    def first_position(self) -> NimPosition:
        return NimPosition(
            lines=self.original_lines,
            next_player=PlayerIndex.FirstPlayer)

    @override
    def next_position(
            self,
            movement: NimMovement,
            position: NimPosition) -> NimPosition:

        next_player = two_player_game_change_player(position.next_player())
        lines = list(position.lines)
        lines[movement.line_index] -= movement.Nim

        return NimPosition(
            lines=lines,
            next_player=next_player
        )

    @override
    def possible_movements(
            self,
            position: NimPosition) -> Iterator[NimMovement]:
        movements_result = []

        for index, line in enumerate(position.lines):

            for i in range(line):

                new_movement = NimMovement(
                    line_index=index,
                    Nim=i+1
                )
                movements_result.append(new_movement)

        return movements_result

    @override
    def finished(
            self,
            position: NimPosition) -> bool:
        return sum(position.lines) == 1

    @override
    def score(
            self,
            position: NimPosition) -> dict[PlayerIndex, float]:
        return {
            position.next_player() : 0.0,
            two_player_game_change_player(position.next_player()) : 1.0
        }
