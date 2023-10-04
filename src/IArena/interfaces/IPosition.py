
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.utils.decorators import pure_virtual

class IPosition:
    """
    Abstract class that represents a position of a game.
    """

    @pure_virtual
    def next_player(
            self) -> PlayerIndex:
        pass
