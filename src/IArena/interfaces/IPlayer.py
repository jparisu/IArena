
from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.IMovement import IMovement
from IArena.utils.decorators import pure_virtual

class IPlayer:
    """
    This abstract class represents a player of a game.
    This player is able to play a movement given any position.
    """

    def __init__(self, name: str = None):
        if name is None:
            name = f'{self.__class__.__name__}_{id(self)}'
        self._name = name

    def name(self) -> str:
        return self._name

    @pure_virtual
    def play(
            self,
            position: IPosition) -> IMovement:
        pass

    def starting_game(
            self,
            rules: IGameRules,
            player_index: int):
        pass
