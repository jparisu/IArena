from typing import Tuple, List
from IArena.utils.decorators import override

from IArena.games.SSP import SSPPosition, SSPMovement, SSPRules
from IArena.interfaces.IPlayer import IPlayer
from IArena.interfaces.IGameRules import IGameRules



class SSPExactPlayer(IPlayer):

    def starting_game(
            self,
            rules: SSPRules,
            player_index: int):

        coins = rules.coins()
        target = rules.target()

        self.indexes_to_select = SSPExactPlayer.__ssp(coins, target)[2]


    @override
    def play(self, position: SSPPosition) -> SSPMovement:

        selected = position.selected()

        if len(selected) == len(self.indexes_to_select):
            return SSPMovement.Finish()
        else:
            next_index = self.indexes_to_select[len(selected)]
            return SSPMovement(coin_index=next_index)


    def __ssp(coins: List[int], target: int) -> Tuple[int, List[int], List[int]]:
        """
        Return (best_sum, subset) where best_sum <= target is maximized
        and subset is one choice of coins achieving best_sum.

        Returns:
        - best_sum: int, the maximum sum achievable not exceeding target
        - subset: List[int], the list of coins that sum up to best_sum
        - indexes: List[int], the list of indexes of the coins in the original list
        """
        dp_states = []
        dp = 1
        mask = (1 << (target + 1)) - 1

        for c in coins:
            if c <= target:
                dp = (dp | (dp << c)) & mask
            dp_states.append(dp)

        best = dp.bit_length() - 1

        # Backtrack a subset that makes 'best'
        subset = []
        indexes = []
        s = best
        for i in range(len(coins) - 1, -1, -1):
            c = coins[i]
            prev_dp = dp_states[i - 1] if i > 0 else 1  # before taking coins[i]
            if c <= s and ((prev_dp >> (s - c)) & 1):
                subset.append(c)
                indexes.append(i)
                s -= c
            # stop early if we hit 0
            if s == 0:
                break

        subset.reverse()
        return best, subset, indexes
