
from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.IMovement import IMovement
from IArena.utils.decorators import pure_virtual

class IPlayer:
    """
    This abstract class represents a player of a game.
    This player is able to play a movement given any position.
    """

    @pure_virtual
    def play(
            self,
            position: IPosition) -> IMovement:
        pass
