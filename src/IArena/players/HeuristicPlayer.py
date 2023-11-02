
from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IPlayer import IPlayer
from IArena.utils.decorators import override, pure_virtual

class HeuristicPlayer(IPlayer):

    @override
    def play(
            self,
            position: IPosition) -> IMovement:
        # Get rules of the game
        rules = position.get_rules()

        # Get all movements
        movements = rules.possible_movements(position)

        # Calculate heuristic for all possible positions from every possible movement
        values = [
            self.heuristic(
                rules.next_position(movement, position))
            for movement
            in movements]

        # Return the best movement
        return movements[values.index(min(values))]

    @pure_virtual
    def heuristic(
            self,
            position: IPosition) -> float:
        pass
