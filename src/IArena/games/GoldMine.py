from __future__ import annotations

from typing import Dict, Iterator, List, Set, Tuple, Iterable
from enum import Enum
from dataclasses import dataclass
from copy import deepcopy

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.interfaces.ScoreBoard import ScoreBoard
from IArena.utils.decorators import override
from IArena.utils.printing import matrix_map_to_str
from IArena.grader.RulesGenerator import IRulesGenerator, RulesGeneratorConfiguration
from IArena.utils.square_map.SquareMap import SquareMap, Coordinate, Direction
from IArena.utils.square_map.draw_square_map import plot_square_map
from IArena.utils.square_map.random_map_generators import MapFactory
from IArena.utils.RandomGenerator import RandomGenerator

"""
This game represents the GoldMine game over a grid map.

The map is unknown to the player, and the tiles must be dug one by one to discover where the gold is.
The tiles close to an already dug tile are called visible tiles.
Each tile has a digging cost, only known when the tile is visible.
The player has a starting position (coordinate unknown) and can move to adjacent tiles (up, down, left, right).
If moved to a tile, the tile is dug and its cost is added to the accumulated cost.

There are different modes for the hints:

1. NO_HINT: No hints are given.
2. COMPASS: The compass gives a direction that points towards the gold.
3. PROXIMITY: The proximity indicates how close the player is to the gold in number of tiles in manhattan distance.
4. DENSITY: The density gives an approximation of the proximity of the gold.
"""

# Alias for a movement cost type
CostType = float

# Alias for square map types
GoldMineDirection = Direction
GoldMineCoordinate = Coordinate
GoldMineSquareMap = SquareMap[CostType]


@dataclass
class GoldMineMovement(IMovement):
    """
    Represent a movement in the GoldMine game.

    It is represented by a direction.

    Attributes
    ----------
    direction : Direction
        The direction of the movement.
    """

    direction: GoldMineDirection

    def __str__(self) -> str:
        """Return a human-readable representation of the movement."""
        return f"<Move {self.direction.name}>"


class GoldMinePosition(IPosition):
    """
    GoldMine game state (position) representation.

    A `GoldMinePosition` encapsulates the *entire* state:
    - Player position
    - Dug tiles

    This implementation is single-player and models a grid exploration / digging process.
    """

    def __init__(
        self,
        rules: GoldMineGameRules,
        current_position: Coordinate,
        digged_tiles: Set[Coordinate],
    ):
        """
        Create a new `GoldMinePosition`.

        Parameters
        ----------
        rules : GoldMineGameRules
            The rules object governing the game logic. This is stored and used to compute:
            - legal movements from this position,
            - accumulated cost,
            - heuristic values,
            - and state transitions.
        current_position : Coordinate
            Current player coordinate on the map.
        digged_tiles : Set[Coordinate]
            Set of tiles already dug (discovered). Must include at least the start tile.
            The set is treated as part of the position state; callers should pass an
            immutable or safely-owned set to avoid unintended side effects.

        Side Effects
        ------------
        - Calls `IPosition.__init__(rules)` to initialize the IArena base class.

        Raises
        ------
        TypeError
            If the provided arguments have incompatible types (depending on runtime checks).
        """
        super().__init__(rules)
        self.__rules: GoldMineGameRules = rules
        self.__current_position = current_position
        self.__digged_tiles = digged_tiles



    ##################################################################################################################
    # STD METHODS

    @override
    def next_player(self) -> PlayerIndex:
        """
        Return the player index that must act next.

        Returns
        -------
        PlayerIndex
            Always `PlayerIndex.FirstPlayer`, since this game is single-player.

        Notes
        -----
        IArena uses this method to determine whose turn it is. For single-player games,
        the value is constant.
        """
        return PlayerIndex.FirstPlayer

    def __eq__(self, other: object) -> bool:
        """
        Equality comparison for positions.

        Two positions are considered equal if they represent the same game state, i.e.:
          - same current coordinate, and
          - same set of dug tiles.

        Parameters
        ----------
        other : GoldMinePosition
            The position to compare against.

        Returns
        -------
        bool
            True if both positions encode the same state; False otherwise.
        """
        if not isinstance(other, GoldMinePosition):
            raise TypeError(f"Cannot compare GoldMinePosition with object of type {type(other)}")
        return (
            self.__current_position == other.__current_position
            and self.__digged_tiles == other.__digged_tiles
        )

    def get_accumulated_cost(self) -> CostType:
        """
        Compute the cumulative digging cost for this state.

        Returns
        -------
        CostType
            Total cost accumulated by digging all tiles contained in `__digged_tiles`.

        Complexity
        ----------
        O(|digged_tiles|), assuming constant-time cost lookup per tile.
        """
        return self.__rules._get_accumulated_cost(self.__digged_tiles)




    ##################################################################################################################
    # HINT METHODS

    def get_compass(self) -> Direction:
        """
        Return the heuristic estimate for the current state.

        Returns
        -------
        CostType
            Heuristic value at `__current_position`, or 0.0 if heuristic mode is disabled.

        Typical Use
        -----------
        Used by informed search algorithms as `h(n)` to guide exploration.
        """
        return self.__rules._get_compass(self.__current_position)


    def get_proximity(self) -> int:
        """
        Return the proximity heuristic for the current state.

        Returns
        -------
        int
            Proximity heuristic value at `__current_position`, or 0 if proximity mode is disabled.

        Typical Use
        -----------
        Used by informed search algorithms as `h(n)` to guide exploration.
        """
        return self.__rules._get_proximity(self.__current_position)


    def get_density(self) -> CostType:
        """
        Return the density heuristic for the current state.

        Returns
        -------
        CostType
            Density heuristic value at `__current_position`, or 0.0 if density mode is disabled.

        Typical Use
        -----------
        Used by informed search algorithms as `h(n)` to guide exploration.
        """
        return self.__rules._get_density(self.__current_position)




    ##################################################################################################################
    # PROTECTED INTERNAL METHODS

    def _already_dug(self, coordinate: Coordinate) -> bool:
        """
        Check if a tile has already been dug.

        Developer Note
        --------------
        This method is meant only to be used from GoldMineGameRules.
        """
        return coordinate in self.__digged_tiles

    def _generate_new_position_from_movement(
        self,
        movement: GoldMineMovement,
    ) -> "GoldMinePosition":
        """
        Produce the successor position after applying a movement.

        Note
        ----
        The movement must be valid from the current position; otherwise, the behavior is undefined.

        Developer Note
        --------------
        This method is meant only to be used from GoldMineGameRules.
        """
        new_coordinate = self.__current_position.from_direction(movement.direction)
        new_digged_tiles = deepcopy(self.__digged_tiles)
        new_digged_tiles.add(new_coordinate)

        return GoldMinePosition(
            self.__rules,
            new_coordinate,
            new_digged_tiles,
        )




    ##################################################################################################################
    # DIRECTION BASED METHODS

    def get_valid_directions(self) -> Iterator[Direction]:
        """
        Generate all legal directions from this position.

        Returns
        -------
        Iterator[Direction]
            An iterator yielding legal movement directions (Up/Down/Left/Right).

        Complexity
        ----------
        Typically O(degree) where degree <= 4 in grid mode, but may be larger in
        omnipresent mode depending on visible frontier size.
        """
        return self.__rules._get_valid_directions(
            self.__current_position,
        )

    def get_cost_from_direction(
        self,
        direction: Direction
    ) -> CostType:
        """
        Get the cost associated with moving in a given direction.

        Parameters
        ----------
        direction : Direction
            The direction for which to obtain the cost.

        Returns
        -------
        CostType
            The cost associated with the specified direction.
        """
        new_coordinate = self.__current_position.from_direction(direction)
        if new_coordinate in self.__digged_tiles:
            return 0.0
        else:
            return self.__rules._get_cost(self.__current_position.from_direction(direction))

    def get_directions_with_cost(self) -> Iterator[Tuple[Direction, CostType]]:
        """
        Generate pairs of valid directions and their associated costs.

        Returns
        -------
        Iterator[Tuple[Direction, CostType]]
            An iterator yielding tuples of (Direction, CostType) for each legal movement direction.
        """
        for direction in self.get_valid_directions():
            cost = self.get_cost_from_direction(direction)
            yield (direction, cost)




    ##################################################################################################################
    # PLOT METHODS

    def __str__(self) -> str:
        """
        Return a human-readable representation of the position.
        It gives the possible directions, along with the cost of each.
        """
        valid_movements = []
        for direction, cost in self.get_directions_with_cost():
            valid_movements.append(f"{direction.name} (cost: {cost})")

        result = "Possible moves:\n  " + "\n  ".join(valid_movements)
        return result

    def _plot_step(
        self,
        axis,
        start: Coordinate,
        target: Coordinate,
        smap: GoldMineSquareMap,
        **kwargs
    ):
        """
        Plot the current game step on the given matplotlib axis.

        Parameters
        ----------
        axis
            The matplotlib axis to plot on.
        start : Coordinate
            The starting coordinate of the game.
        target : Coordinate
            The target coordinate of the game.
        smap : GoldMineSquareMap
            The underlying cost map of the game, used for visualization.
        **kwargs
            Additional keyword arguments for visualization customization (e.g., colors, markers).

        Developer Note
        --------------
        This method is meant only to be used from GoldMineGameRules.
        """

        plot_square_map(
            axis=axis,
            square_map=smap,
            start=self.__current_position,
            target=target,
            empty_tiles=self.__digged_tiles,
            cost=self.get_accumulated_cost(),
            **kwargs
        )


##################################################################################################################
##################################################################################################################

class GoldMineGameRules(IGameRules):
    """
    Represents the rules of the GoldMine game.

    In this implementation, the rules define the map, the target coordinate and the starting coordinate.
    The logic of digged tiles and movement is handled in the Position class.
    """

    def __init__(
        self,
        map: GoldMineSquareMap,
        target: Coordinate,
        start: Coordinate = Coordinate(0, 0),
        compass_activated: bool = False,
        proximity_activated: bool = False,
        density_activated: bool = False,
        heuristic_map: GoldMineSquareMap = None
    ):
        """Initialize rules: map/target/start plus optional heuristic modes."""
        self.__map : GoldMineSquareMap = deepcopy(map)
        self.__target : Coordinate = deepcopy(target)
        self.__start : Coordinate = deepcopy(start)

        self.__compass_activated : bool = compass_activated
        self.__proximity_activated : bool = proximity_activated
        self.__density_activated : bool = density_activated

        self.__heuristic_map : GoldMineSquareMap = heuristic_map if heuristic_map is not None else GoldMineSquareMap.zeros_like(self.__map)

        # Check map
        self.__map.check(
            allow_zero=False,
            skip_coordinate_validation=[self.__start]
        )

    ##################################################################################################################
    # STD METHODS

    @override
    def n_players(self) -> int:
        """Return number of players (single-player here)."""
        return 1

    @override
    def first_position(self) -> GoldMinePosition:
        """Return the initial position for a new game instance."""
        return GoldMinePosition(self, self.__start, {self.__start})

    @override
    def next_position(
        self,
        movement: GoldMineMovement,
        position: GoldMinePosition
    ) -> GoldMinePosition:
        """Apply a movement to a position and return the resulting successor position."""
        return position._generate_new_position_from_movement(
            movement,
        )

    @override
    def possible_movements(
        self,
        position: GoldMinePosition
    ) -> Iterator[GoldMineMovement]:
        """Yield the legal movement objects from the given position (dropping direction/cost)."""
        for dir in position.get_valid_directions():
            yield GoldMineMovement(dir)

    @override
    def finished(self, position: GoldMinePosition) -> bool:
        """Return True if the game is finished in this position (target already dug)."""
        return position._already_dug(self.__target)

    @override
    def score(self, position: GoldMinePosition) -> ScoreBoard:
        """Return a scoreboard value for terminal evaluation (negative cost => lower is worse)."""
        sb = ScoreBoard()
        sb.define_score(PlayerIndex.FirstPlayer, -position.get_accumulated_cost())
        return sb

    ##################################################################################################################
    # GET METHODS FOR RULES ATTRIBUTES

    def compass_activated(self) -> bool:
        """Return True if compass heuristic is activated."""
        return self.__compass_activated

    def proximity_activated(self) -> bool:
        """Return True if proximity heuristic is activated."""
        return self.__proximity_activated

    def density_activated(self) -> bool:
        """Return True if density heuristic is activated."""
        return self.__density_activated


    ##################################################################################################################
    # PROTECTED METHODS FOR POSITION INTERACTIONS WITH MAP

    def _get_accumulated_cost(self, digged_tiles: Iterable[Coordinate]) -> CostType:
        """
        Compute total cost over all dug tiles using the underlying cost map.

        Developer Note
        --------------
        This method is meant only to be used from GoldMinePosition.
        """
        total_cost = 0.0
        for coord in digged_tiles:
            total_cost += self.__map[coord]
        return CostType(total_cost)

    def _get_density(self, coordinate: Coordinate) -> CostType:
        """
        Return density value for a coordinate if enabled, otherwise fail.

        Developer Note
        --------------
        This method is meant only to be used from GoldMinePosition.
        """
        if not self.__density_activated:
            raise RuntimeError("Density heuristic is not activated.")
        return self.__heuristic_map[coordinate]

    def _get_compass(self, coordinate: Coordinate) -> Direction:
        """
        Return compass direction for a coordinate if enabled, otherwise fail.

        Developer Note
        --------------
        This method is meant only to be used from GoldMinePosition.
        """
        if not self.__compass_activated:
            raise RuntimeError("Compass heuristic is not activated.")
        return self.__map.compass_direction(coordinate, self.__target)

    def _get_proximity(self, coordinate: Coordinate) -> int:
        """
        Return proximity value for a coordinate if enabled, otherwise fail.

        Developer Note
        --------------
        This method is meant only to be used from GoldMinePosition.
        """
        if not self.__proximity_activated:
            raise RuntimeError("Proximity heuristic is not activated.")
        return abs(coordinate.x - self.__target.x) + abs(coordinate.y - self.__target.y)

    def _get_valid_directions(self, coordinate: Coordinate) -> Iterator[Direction]:
        """
        Yield all valid movement directions from the given coordinate.

        Developer Note
        --------------
        This method is meant only to be used from GoldMinePosition.
        """
        for direction in self.__map.possible_directions(coordinate):
            yield direction

    def _get_cost(
        self,
        coordinate: Coordinate
    ) -> CostType:
        """
        Return the cost of digging at the given coordinate.

        Developer Note
        --------------
        This method is meant only to be used from GoldMinePosition.
        """
        return self.__map[coordinate]

    ##################################################################################################################

    ##################################################################################################################
    # VISUALIZATION METHODS

    def plot_step(
        self,
        axis,
        position: GoldMinePosition,
        **kwargs
    ):
        """Plot the current game step on the given matplotlib axis."""
        position._plot_step(
            axis=axis,
            start=self.__start,
            target=self.__target,
            smap=self.__map,
            **kwargs
        )



class GoldMineGenerator(IRulesGenerator):

    def generate(self, configuration: RulesGeneratorConfiguration) -> GoldMineGameRules:

        map_height = IRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['n', 'map_height', 'rows', 'row', 'height'],
            required = True,
            type_cast = int,
        )

        map_width = IRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['m', 'map_width', 'cols', 'col', 'width'],
            required = True,
            type_cast = int,
        )

        compass_activated = IRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['compass_activated', 'compass'],
            default_value = False,
            type_cast = bool,
        )

        proximity_activated = IRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['proximity_activated', 'proximity'],
            default_value = False,
            type_cast = bool,
        )

        density_activated = IRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['density_activated', 'density'],
            default_value = False,
            type_cast = bool,
        )

        starting_position = IRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['starting_position', 'start'],
            default_value = Coordinate(0, 0),
            type_cast = Coordinate,
        )

        target_position = IRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['target_position', 'target'],
            default_value = None,
            type_cast = Coordinate,
        )  # If target position is none, it is set randomly later on

        seed = IRulesGenerator._get_param(
            configuration=configuration,
            param_name = 'seed',
            default_value = None,
            type_cast = int,
        )

        map_configuration = IRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['map', 'map_configuration'],
            default_value = {},
        )

        map_generator = IRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['map_generator', 'map_gen'],
            default_value = 'uniform',
            type_cast = str,
        )

        integer = IRulesGenerator._get_param(
            configuration=configuration,
            param_name = 'integer',
            default_value = True,
            type_cast = bool,
        )


        # GENERATE RANDOM GENERATOR
        rng = RandomGenerator(seed)

        # GENERATE START POSITION
        # If starting coordinate is negative, means to generate it randomly
        if starting_position.x < 0 or starting_position.y < 0:
            starting_position = Coordinate(
                x=rng.randint(map_height),
                y=rng.randint(map_width)
            )

        # GENERATE TARGET POSITION
        while target_position is None or target_position == starting_position:
            target_position = Coordinate(
                x=rng.randint(map_height),
                y=rng.randint(map_width)
            )

        # GENERATE MAP
        grid = MapFactory.generate(
            name=map_generator,
            n=map_height,
            m=map_width,
            start=starting_position,
            target=target_position,
            rng=rng,
            integer=integer,
            **map_configuration,
        )

        # Set starting position as 0 cost
        grid[starting_position.as_tuple()] = 0.0

        square_map = SquareMap(grid)

        return GoldMineGameRules(
            map=square_map,
            target=target_position,
            start=starting_position,
            compass_activated=compass_activated,
            proximity_activated=proximity_activated,
            density_activated=density_activated,
            heuristic_map=None,  # TODO: generate heuristic map if needed
        )
