
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.utils.decorators import pure_virtual

class IPosition:
    """
    Abstract class that represents a position of a game.
    """

    def __init__(self, rules: "IGameRules"):
        self.rules = rules

    @pure_virtual
    def next_player(
            self) -> PlayerIndex:
        pass

    def get_rules(self) -> "IGameRules":
        """Get the rules of the game."""
        return self.rules


CostType = float

class CostPosition(IPosition):
    """
    Abstract class that represents a position of a game that has a cost.
    This is very useful for one player games.
    """

    def __init__(self, rules: "IGameRules", cost: CostType):
        super().__init__(rules)
        self._cost = cost

    def cost(self) -> CostType:
        return self._cost

    def __eq__(self, other: "CostPosition"):
        return self._cost == other._cost

    def __str__(self):
        return f"Cost: {self._cost}"
