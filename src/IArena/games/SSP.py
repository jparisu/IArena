
from typing import Iterator, List, Set
from copy import deepcopy
from dataclasses import dataclass

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.IPlayer import IPlayer
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.utils.decorators import override
from IArena.interfaces.ScoreBoard import ScoreBoard
from IArena.grader.RulesGenerator import IRulesGenerator

"""
This game represents the Subset Sum Problem (SSP) as a one-player game
There is a set of n coins, each with a positive value.
The player should select a subset of these coins such that their sum is as close as possible to a target value T without exceeding it.
Each movement the player selects a coin that has not been selected before.
"""

class SSPPosition(IPosition):
    """Represents a list of coins (integers) available to select from."""

    def __init__(
                self,
                rules: "IGameRules",
                selected: Set[int],
                finished: bool = False):
        super().__init__(rules)
        self.selected_ = selected
        self.finished_ = finished

    @override
    def next_player(
            self) -> PlayerIndex:
        return PlayerIndex.FirstPlayer

    def coins(self) -> List[int]:
        return self.get_rules().coins()

    def selected(self) -> Set[int]:
        return deepcopy(self.selected_)

    def __eq__(self, other: "SSPPosition"):
        return self.coins_ == other.coins_

    def __str__(self):
        # Create a table with coins and if they are selected or not
        coins = self.coins()
        selected = self.selected()
        st = ""
        st += f"Coins   : |"
        for c in coins:
            st += f" {c:4} |"
        st += "\n"
        st += f"Selected: | "
        for i in range(len(coins)):
            if i in selected:
                st += "   X | "
            else:
                st += "     | "
        st += "\n"
        st += f"Target: {str(self.get_rules().target())} | Current Sum: {(self.get_rules().coins_value(self))}\n"
        return st



class SSPMovement(IMovement):
    """Represents the selection of a subset of coins by their indices."""

    def __init__(
                self,
                coin_index: int = None,
                finish: bool = False):
        self.coin_index = coin_index
        self.finish = finish

    def __eq__(
            self,
            other: "SSPMovement") -> bool:
        return self.coin_index == other.coin_index and self.finish == other.finish

    def __str__(self) -> str:
        if self.finish:
            return "{Finish}"
        else:
            return f"{{Select coin index {self.coin_index}}}"

    def Finish() -> "SSPMovement":
        return SSPMovement(finish=True)



class SSPRules(IGameRules):
    """Rules for Subset Sum Problem game."""

    def __init__(
            self,
            coins: List[int],
            target: int):

        self.coins_ = coins
        self.target_ = target

    @override
    def n_players(self) -> int:
        return 1

    @override
    def first_position(self) -> SSPPosition:
        return SSPPosition(self, set(), False)


    @override
    def next_position(
            self,
            movement: SSPMovement,
            position: SSPPosition) -> SSPPosition:
        if movement.finish:
            return SSPPosition(self, position.selected(), True)

        else:
            # Check if the coin index is valid
            if movement.coin_index < 0 or movement.coin_index >= len(self.coins_):
                raise ValueError(f"Invalid coin index {movement.coin_index}.")

            # Check if the coin has already been selected
            if movement.coin_index in position.selected():
                raise ValueError(f"Coin index {movement.coin_index} has already been selected.")

            # Create a new position with the selected coin added
            new_selected = position.selected()
            new_selected.add(movement.coin_index)
            return SSPPosition(self, new_selected)


    @override
    def possible_movements(
            self,
            position: SSPPosition) -> Iterator[SSPMovement]:
        if position.finished_:
            return iter([])
        else:
            # Possible movements are selecting any unselected coin or finishing the selection
            unselected_indices = [i for i in range(len(self.coins_)) if i not in position.selected()]
            for index in unselected_indices:
                yield SSPMovement(coin_index=index)
            yield SSPMovement(finish=True)


    @override
    def finished(
            self,
            position: SSPPosition) -> bool:
        return position.finished_ or self.coins_value(position) >= self.target_


    @override
    def score(
            self,
            position: SSPPosition) -> ScoreBoard:

        coins_sum = self.coins_value(position)
        if coins_sum > self.target_:
            coins_sum = 0

        s = ScoreBoard()
        s.define_score(PlayerIndex.FirstPlayer, coins_sum)
        return s


    def coins(self) -> List[int]:
        return deepcopy(self.coins_)

    def target(self) -> int:
        return self.target_


    def coins_value(self, position: SSPPosition) -> int:
        return sum(self.coins_[i] for i in position.selected())



class SSPPlayablePlayer(IPlayer):

    SeparatorN = 60

    @override
    def play(
            self,
            position: SSPPosition) -> SSPMovement:

        possibilities = list(position.get_rules().possible_movements(position))

        print ("=" * SSPPlayablePlayer.SeparatorN)
        print (f"Index   : |", end="")
        for i in range(len(position.coins())):
            print (f" {i:4} |", end="")
        print ()
        print (position)
        print ("-" * SSPPlayablePlayer.SeparatorN)

        move = -1

        while True:

            move = int(input("Select an index that has not been selected yet, or -1 to finish the selection: "))

            if move == -1:
                return SSPMovement(finish=True)
            else:
                if move < 0 or move >= len(position.coins()):
                    print(f"Invalid index {move}. Try again.")
                elif move in position.selected():
                    print(f"Index {move} has already been selected. Try again.")
                else:
                    return SSPMovement(coin_index=move)



class SSPRulesGenerator(IRulesGenerator):

    @override
    def generate(
            self,
            configuration: dict) -> IGameRules:

        target = SSPRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['target', 'T'],
            required = True,
            type_cast = int,
        )

        coins = SSPRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['coins', 'numbers'],
            required = True,
        )

        return SSPRules(
            coins = coins,
            target = target
        )
