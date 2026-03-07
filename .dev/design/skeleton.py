"""Library skeleton generated from docs/design/class-diagram.puml/structure.puml."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Generic, Iterable, Iterator, List, Mapping, MutableSequence, Protocol, Sequence, TypeVar, Tuple, overload
import numpy as np

Map = dict[str, Any]
ScoreBoardPair = tuple["ScoreBoard", "ScoreBoard"]
T = TypeVar("T")
ParametrizedType = TypeVar("ParametrizedType")
ParameterType = TypeVar("ParameterType", bound="GenericParameter")



# region utilizing.protocoling

class Hashable(Protocol):
    """Protocol for objects that can be hashed and compared in collections."""

    @abstractmethod
    def hash(self) -> int:
        """Return an integer hash representation of the object."""
        ...

class Recognizable(Protocol):
    """Protocol for objects that expose a recognizable name."""

    @abstractmethod
    def name(self) -> str:
        """Return the display or identifier name of the object."""
        ...

# endregion


# region utilizing.randoming

class RandomGenerator:
    """Random generator abstraction used to centralize reproducible randomness."""

    def __init__(self, seed: int | None = 0) -> None:
        """Initialize the random generator with an optional seed."""
        ...

    def rand(self) -> float:
        """Return a pseudo-random floating-point number in [0, 1)."""
        ...

    def random(self) -> float:
        """Return a pseudo-random floating-point number in [0, 1)."""
        ...

    def choice(self, seq: Sequence[T]) -> T:
        """Return one random element selected from a non-empty sequence."""
        ...

    def set_seed(self, seed: int, consistent: bool = False) -> None:
        """Set the generator seed and optionally update consistency tracking."""
        ...

    def reset_seed(self) -> None:
        """Reset the generator to its initial seed value."""
        ...

    def shuffle(self, x: MutableSequence[T]) -> None:
        """Shuffle a mutable sequence in-place using this generator."""
        ...

    def randint(self, high: int, low: int = 0) -> int:
        """Return a pseudo-random integer sampled from [low, high)."""
        ...

class Perlin:
    """Perlin noise utility class exposing static generation helpers."""

    @classmethod
    def perlin_value_generator(
        i: int,
        j: int,
        base: int,
        scale: float,
        persistence: float = 0.5,
        octaves: int = 2,
        lacunarity: float = 2.0,
    ) -> float:
        """Generate one Perlin noise value for a coordinate."""
        ...

    @classmethod
    def perlin_generator(
        n: int,
        m: int,
        abruptness: float = 0.5,
        rng: RandomGenerator | None = None,
    ) -> np.ndarray:
        """Generate a matrix of Perlin-like noise values."""
        ...

# endregion


# region utilizing.timing

class Timer:
    """Timer helper to track elapsed time and enforce timeouts."""

    def __init__(self, start_activated: bool = True) -> None:
        """Initialize the timer and optionally start it immediately."""
        ...

    def start(self) -> None:
        """Start the timer if it is currently paused."""
        ...

    def pause(self) -> None:
        """Pause the timer and accumulate elapsed time."""
        ...

    def reset(self) -> None:
        """Reset the accumulated timer value and keep current running mode."""
        ...

    def elapsed(self) -> float:
        """Return total elapsed time in seconds."""
        ...

class Worker:
    """Worker utility to execute callables with an execution time limit."""

    @classmethod
    def limited_time_call(func: Callable[..., Any], timeout_s: float, *args: Any) -> Any:
        """Run a callable with positional arguments under a timeout in seconds."""
        ...

# endregion


# region utilizing.structuring

class GenericRegistry(ABC, Generic[T]):
    """Generic alias-aware registry for storing values by normalized names."""

    def __init__(self, name_convention: Callable[[str], str] | None = None) -> None:
        """Initialize storage and alias maps with an optional naming convention."""
        ...

    def register(
        self,
        obj: T,
        name: str,
        aliases: Sequence[str] | None = None,
        overwrite: bool = False,
    ) -> str:
        """Register a value with one primary name and optional aliases."""
        ...

    def register_alias(self, alias: str, target_existing_alias: str, overwrite: bool = False) -> None:
        """Register an alias pointing to an already registered alias or name."""
        ...

    def get(self, name: str, strict: bool = True) -> T | None:
        """Retrieve a registered value by name or alias."""
        ...

    def remove_alias(self, name: str) -> None:
        """Remove one alias without deleting the underlying stored value."""
        ...

    def remove_value(self, name: str) -> T | None:
        """Remove a stored value and every alias that points to it."""
        ...

    def has(self, name: str) -> bool:
        """Return whether a given name or alias is registered."""
        ...

    def list_aliases(self) -> List[str]:
        """Return all registered aliases."""
        ...

    def __contains__(self, name: str) -> bool:
        """Return whether the registry contains a given name or alias."""
        ...

    def __len__(self) -> int:
        """Return the number of unique stored values."""
        ...

    def clear(self) -> None:
        """Remove all stored values and aliases."""
        ...

class GenericFactory(GenericRegistry[Callable[..., T]], ABC):
    """Factory registry that stores constructors and creates instances by name."""

    def register_constructor(
        self,
        constructor: Callable[..., T],
        name: str,
        aliases: List[str] | None = None,
        overwrite: bool = False,
    ) -> None:
        """Register a constructor under one name and optional aliases."""
        ...

    def construct(self, name: str, **kwargs: Any) -> T:
        """Construct and return an instance using the constructor bound to name."""
        ...

class GenericSingleton(Generic[T]):
    """Generic singleton wrapper that lazily creates one instance per class."""

    def __init__(self, cls: type[T]) -> None:
        """Initialize singleton wrapper for the provided class."""
        ...

    def __call__(self, *args: object, **kwargs: object) -> T:
        """Return the singleton instance, creating it on first invocation."""
        ...

    def get_instance(self) -> T:
        """Return the singleton instance via explicit getter."""
        ...

class GenericEnumRegistry(Enum):
    """Enum helper base adding normalized lookup and alias support."""

    @classmethod
    def get_all_values(cls) -> List[Any]:
        """Return the list of values for all enum members."""
        ...

    def get(self, index: int | None = None) -> Any:
        """Return member value or indexed item when value is a sequence."""
        ...

    @classmethod
    def find(cls: type[T], query: str, throw: bool = True, only_keys: bool = False) -> T | None:
        """Find and return a member matching query by key or value."""
        ...

    @classmethod
    def from_string(cls: type[T], value: str, throw: bool = True) -> T | None:
        """Resolve an enum member from its string representation."""
        ...

    @classmethod
    def name_convention(cls, name: str) -> str:
        """Normalize a name using alias resolution and naming conventions."""
        ...

    @classmethod
    def default(cls) -> T | None:
        """Return the default enum member when available."""
        ...

    @classmethod
    def aliases(cls) -> dict[str, str]:
        """Return alias mappings for enum member names."""
        ...

class GenericParameter:
    """Dataclass-oriented parameter base with typed update and serialization helpers."""

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        """Build a parameter instance from a dictionary."""
        ...

    def update_from_dict(self: T, data: Mapping[str, Any]) -> T:
        """Update current parameter fields from a mapping."""
        ...

    def _convert_value(self, target_type: Any, value: Any) -> Any:
        """Convert one value to its target type with helper hooks."""
        ...

    def to_dict(self, target_format: str | None = None) -> dict[str, Any]:
        """Serialize current parameter values to a dictionary."""
        ...

    def set_default_value(self, field_name: str, default_value: Any) -> None:
        """Set a field default only when the field currently holds None."""
        ...

    @classmethod
    def aliases(cls) -> dict[str, str]:
        """Return alias mapping from external keys to field names."""
        ...

    def copy(self: T) -> T:
        """Return a copied parameter instance."""
        ...

class GenericSuiteParameter(Generic[ParameterType]):
    """Suite wrapper that expands fixed and list-based inputs into concrete parameter instances."""

    parameter_cls: type[ParameterType]
    fixed_values: dict[str, Any]
    suite_values: dict[str, List[Any]]

    def __init__(
        self,
        parameter_cls: type[ParameterType],
        fixed_values: Mapping[str, Any],
        suite_values: Mapping[str, Sequence[Any]],
    ) -> None:
        """Store the target parameter class and the parsed fixed/suite values."""
        ...

    @classmethod
    def from_dict(
        cls,
        parameter_cls: type[ParameterType],
        src: Mapping[str, Any],
        *,
        suite_prefix: str = "suite:",
        treat_plain_lists_as_suite: bool = True,
    ) -> GenericSuiteParameter[ParameterType] | ParameterType:
        """Parse a source map into either one parameter instance or a suite wrapper."""
        ...

    def to_dict(self, target_format: str | None = None) -> dict[str, Any]:
        """Serialize current parameter values to a dictionary."""
        ...

    def length(self) -> int:
        """Return the number of concrete parameter combinations in the suite."""
        ...

    def individual_parameters(self) -> Iterator[ParameterType]:
        """Yield one concrete parameter instance per suite combination."""
        ...

    def individual_parameter(self) -> Iterator[ParameterType]:
        """Backward-compatible alias for `individual_parameters`."""
        ...

# endregion


# region utilizing.mapping.square_map

class SquareMapDirection(Enum):
    """Cardinal movement direction for square-grid traversal."""

    @property
    def delta(self) -> tuple[int, int]:
        """Return movement delta `(dx, dy)` represented by the direction."""
        ...

    def opposite(self) -> SquareMapDirection:
        """Return the opposite cardinal direction."""
        ...

class SquareMapCoordinate:
    """Square-grid coordinate with neighbor and distance helpers."""

    x: int
    y: int

    @classmethod
    def from_tuple(cls, value: tuple[int, int]) -> SquareMapCoordinate:
        """Build a coordinate instance from a `(row, col)` tuple."""
        ...

    def up(self) -> SquareMapCoordinate:
        """Return the coordinate one row above."""
        ...

    def down(self) -> SquareMapCoordinate:
        """Return the coordinate one row below."""
        ...

    def left(self) -> SquareMapCoordinate:
        """Return the coordinate one column to the left."""
        ...

    def right(self) -> SquareMapCoordinate:
        """Return the coordinate one column to the right."""
        ...

    def moved(self, direction: SquareMapDirection) -> SquareMapCoordinate:
        """Return the coordinate moved by one step in the given direction."""
        ...

    def from_direction(self, direction: SquareMapDirection) -> SquareMapCoordinate:
        """Return the coordinate moved in the given direction (compatibility alias)."""
        ...

    def manhattan_distance(self, other: SquareMapCoordinate) -> int:
        """Return the Manhattan distance to another coordinate."""
        ...

    def as_tuple(self) -> tuple[int, int]:
        """Return the coordinate as a `(row, col)` tuple."""
        ...

    def __iter__(self) -> Iterator[int]:
        """Iterate coordinate components in `(x, y)` order."""
        ...

    def __len__(self) -> int:
        """Return tuple-like length for coordinate unpacking semantics."""
        ...

    def __getitem__(self, index: int) -> int:
        """Return tuple-like indexed coordinate component."""
        ...

    def neighbors(self) -> Iterator[tuple[SquareMapDirection, SquareMapCoordinate]]:
        """Yield four cardinal neighbors as direction-coordinate pairs."""
        ...

class SquareMap(Generic[T]):
    """Rectangular square-grid wrapper with navigation and numeric helpers."""

    def __init__(self, smap: Iterable[Iterable[T]]) -> None:
        """Initialize the map from an iterable of equally sized rows."""
        ...

    def __str__(self) -> str:
        """Return the text representation of the map."""
        ...

    def pretty_text(self) -> str:
        """Render map contents as aligned multiline text."""
        ...

    def size(self) -> tuple[int, int]:
        """Return map shape as `(n_rows, n_cols)`."""
        ...

    def n_rows(self) -> int:
        """Return number of rows in the map."""
        ...

    def n_cols(self) -> int:
        """Return number of columns in the map."""
        ...

    def __len__(self) -> int:
        """Return number of rows in the map."""
        ...

    def __iter__(self) -> Iterator[List[T]]:
        """Iterate row lists in row-major order."""
        ...

    def __getitem__(self, index: SquareMapCoordinate) -> T:
        """Return value stored at a coordinate index."""
        ...

    def __setitem__(self, index: SquareMapCoordinate, value: T) -> None:
        """Set value at a coordinate index."""
        ...

    def in_bounds(self, coord: SquareMapCoordinate) -> bool:
        """Return whether a coordinate lies within map boundaries."""
        ...

    def require_in_bounds(self, coord: SquareMapCoordinate, *, name: str = "coordinate") -> None:
        """Raise an error if a coordinate is outside map boundaries."""
        ...

    def get(self, coord: SquareMapCoordinate, default: T | None = None) -> T | None:
        """Return map value at coordinate or fallback default when out-of-bounds."""
        ...

    def possible_direction_neighbors(self, coord: SquareMapCoordinate) -> Iterator[tuple[SquareMapDirection, SquareMapCoordinate]]:
        """Yield in-bounds neighbors with their associated directions."""
        ...

    def possible_directions(self, coord: SquareMapCoordinate) -> Iterator[SquareMapDirection]:
        """Yield valid movement directions from a coordinate."""
        ...

    def possible_neighbors(self, coord: SquareMapCoordinate) -> Iterator[SquareMapCoordinate]:
        """Yield valid neighboring coordinates from a coordinate."""
        ...

    def iter_coordinates(self) -> Iterator[SquareMapCoordinate]:
        """Iterate every coordinate in row-major order."""
        ...

    def iter_values(self) -> Iterator[T]:
        """Iterate every stored value in row-major order."""
        ...

    def check(
        self,
        allow_zero: bool = True,
        skip_coordinate_validation: Iterable[SquareMapCoordinate] | None = None,
    ) -> None:
        """Validate numeric sign constraints for map values."""
        ...

    @classmethod
    def full(cls, n_rows: int, n_cols: int, value: T) -> SquareMap[T]:
        """Build a map filled with one constant value."""
        ...

    @classmethod
    def zeros(cls, n_rows: int, n_cols: int) -> SquareMap[float]:
        """Build a floating-point zero map with the requested shape."""
        ...

    @classmethod
    def zeros_like(cls, smap: SquareMap[object]) -> SquareMap[float]:
        """Build a floating-point zero map with the same shape as another map."""
        ...

    @classmethod
    def from_numpy(cls, array: np.ndarray) -> SquareMap[float]:
        """Build a map from a two-dimensional array-like object."""
        ...

    def to_numpy(self, *, dtype: Any = float) -> np.ndarray:
        """Export map contents to an array object with the selected dtype."""
        ...

    def copy(self) -> SquareMap[T]:
        """Return a deep copy of the map rows."""
        ...

    def compass_direction(self, from_coord: SquareMapCoordinate, to_coord: SquareMapCoordinate) -> SquareMapDirection:
        """Return dominant cardinal direction from one coordinate to another."""
        ...

    def min(self) -> float:
        """Return the minimum numeric value in the map."""
        ...

    def max(self) -> float:
        """Return the maximum numeric value in the map."""
        ...

    def sum(self) -> float:
        """Return the sum of numeric values in the map."""
        ...

# endregion


# region utilizing.mapping.square_map.generators

class AbstractMapGenerator(ABC):
    """Abstract base for square-map generator strategies."""

    @classmethod
    @abstractmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: SquareMapCoordinate,
        target: SquareMapCoordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> np.ndarray:
        """Generate a square-map grid for given dimensions, endpoints, and options."""
        ...

    @classmethod
    def _validate_dims(n: int, m: int) -> None:
        """Validate grid dimensions are strictly positive."""
        ...

    @classmethod
    def _validate_coordinate(n: int, m: int, coordinate: SquareMapCoordinate, label: str) -> None:
        """Validate that a coordinate lies within the provided dimensions."""
        ...

    @classmethod
    def _validate_probability(p: float) -> None:
        """Validate that a probability value lies in the interval [0, 1]."""
        ...

    @classmethod
    def _uniform01(rng: RandomGenerator) -> float:
        """Return one uniform random value in [0, 1)."""
        ...

    @classmethod
    def _uniform(cls, rng: RandomGenerator, low: float, high: float) -> float:
        """Return one uniform random value in [low, high)."""
        ...

    @classmethod
    def _exponential(cls, rng: RandomGenerator, scale: float = 1.0) -> float:
        """Return one exponentially distributed sample with the given scale."""
        ...

    @classmethod
    def _has_path_4neigh(grid: np.ndarray, start: SquareMapCoordinate, target: SquareMapCoordinate) -> bool:
        """Return whether a 4-neighborhood path exists between start and target."""
        ...

    @classmethod
    def _carve_manhattan_path(grid: np.ndarray, start: SquareMapCoordinate, target: SquareMapCoordinate) -> None:
        """Carve an in-place Manhattan path from start to target."""
        ...

    @classmethod
    def _set_random_high_tiles(
        cls,
        grid: np.ndarray,
        rng: RandomGenerator,
        p: float,
        high_cost: float,
        avoid: Iterable[SquareMapCoordinate] | None,
    ) -> None:
        """Set random cells to a high traversal cost while avoiding selected coordinates."""
        ...

class EmptyMap(AbstractMapGenerator):
    """Map generator that returns a fully walkable uniform-cost grid."""

    @classmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: SquareMapCoordinate,
        target: SquareMapCoordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> np.ndarray:
        """Generate an empty map where all cells share the same base cost."""
        ...

class UniformMap(AbstractMapGenerator):
    """Map generator that samples costs from a uniform distribution."""

    @classmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: SquareMapCoordinate,
        target: SquareMapCoordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> np.ndarray:
        """Generate a map with independent uniformly sampled cell costs."""
        ...

class BimodelMap(AbstractMapGenerator):
    """Map generator with low-cost and high-cost terrain states."""

    @classmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: SquareMapCoordinate,
        target: SquareMapCoordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> np.ndarray:
        """Generate a bimodal-cost map with stochastic high-cost placement."""
        ...

class ColumnMap(AbstractMapGenerator):
    """Map generator that ensures connectivity between start and target."""

    @classmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: SquareMapCoordinate,
        target: SquareMapCoordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> np.ndarray:
        """Generate a connected map and carve fallback path when needed."""
        ...

class ExponentialMap(AbstractMapGenerator):
    """Map generator that samples costs from an exponential distribution."""

    @classmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: SquareMapCoordinate,
        target: SquareMapCoordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> np.ndarray:
        """Generate a map with exponential random costs shifted above one."""
        ...

class JumpingMap(AbstractMapGenerator):
    """Map generator that preserves walkable endpoints while adding high-cost tiles."""

    @classmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: SquareMapCoordinate,
        target: SquareMapCoordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> np.ndarray:
        """Generate a map that guarantees start and target remain walkable."""
        ...

class PerlinMap(AbstractMapGenerator):
    """Map generator that produces smooth Perlin-like terrain costs."""

    @classmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: SquareMapCoordinate,
        target: SquareMapCoordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> np.ndarray:
        """Generate a smooth noise-based cost map normalized to target range."""
        ...

class MapFactory:
    """Factory registry for square-map generation strategies."""

    @classmethod
    def register(cls, name: str, generator: type[AbstractMapGenerator]) -> None:
        """Register or override a named generator class."""
        ...

    @classmethod
    def unregister(cls, name: str) -> None:
        """Unregister a named generator class from the factory."""
        ...

    @classmethod
    def generate(
        cls,
        name: str,
        n: int,
        m: int,
        start: SquareMapCoordinate,
        target: SquareMapCoordinate,
        rng: RandomGenerator,
        integer: bool = False,
        **kwargs: Any,
    ) -> np.ndarray:
        """Generate a map by method name and optional generator-specific arguments."""
        ...

    @classmethod
    def available_generation_methods(cls) -> List[str]:
        """Return the canonical list of available generation method names."""
        ...

# endregion


# region gaming

class Movement(ABC):
    """Abstract representation of a movement connecting two game states."""

class Position(Hashable, ABC):
    """Abstract representation of a game state position."""

    @abstractmethod
    def next_player(self) -> PlayerIndex:
        """Return the player index that should act from this position."""
        ...

    @abstractmethod
    def get_rules(self) -> Rules:
        """Return the rules instance associated with this position."""
        ...

class Configuration(GenericParameter, ABC):
    """Abstract configuration object used to construct game rules."""

class ConfigurationSuite(GenericSuiteParameter["Configuration"], ABC):
    """Abstract configuration suite that generates multiple game configurations."""

    @classmethod
    def from_dict(
        cls,
        parameter_cls: type[Configuration],
        src: Mapping[str, Any],
        *,
        suite_prefix: str = "suite:",
        treat_plain_lists_as_suite: bool = True,
    ) -> ConfigurationSuite | Configuration:
        """Parse a dictionary as either one configuration or a suite of configurations."""
        ...

    @abstractmethod
    def generate_configurations(self) -> Iterator[Configuration]:
        """Yield each concrete configuration from the suite product."""
        ...

    @abstractmethod
    def length(self) -> int:
        """Return the number of concrete configurations in the suite."""
        ...

class Rules(ABC):
    """Abstract stateless rules engine encapsulating game logic."""

    @abstractmethod
    def n_players(self) -> int:
        """Return the number of players supported by the game."""
        ...

    @abstractmethod
    def first_position(self) -> Position:
        """Return the initial position of a new game."""
        ...

    @abstractmethod
    def next_position(self, pos: Position, mov: Movement) -> Position:
        """Return the next position after applying a movement."""
        ...

    @abstractmethod
    def possible_movements(self, pos: Position) -> Iterator[Movement]:
        """Yield all legal movements available from a position."""
        ...

    @abstractmethod
    def is_finished(self, pos: Position) -> bool:
        """Return whether the game is finished at a position."""
        ...

    @abstractmethod
    def get_score(self, pos: Position) -> ScoreBoard:
        """Return the scoreboard value for a position."""
        ...

class Oracle:
    """Resolver that computes min and max benchmark scores for a game."""

    @classmethod
    def reckon_solution_score(cls, rules: Rules) -> ScoreBoardPair:
        """Compute best and worst attainable scoreboards for given rules."""
        ...

class Game(Recognizable):
    """Game registry and factory entry point exposing supported components."""

    def get_configurations(self, requirements: Callable[[Any], bool]) -> set[type[Configuration]]:
        """Return supported configuration classes for the game."""
        ...

    def get_rules(self, requirements: Callable[[Any], bool]) -> set[type[Rules]]:
        """Return supported rules classes for the game."""
        ...

    def get_oracles(self, requirements: Callable[[Any], bool]) -> set[type[Oracle]]:
        """Return supported oracle classes for the game."""
        ...

    def get_players(self, requirements: Callable[[Any], bool]) -> set[type[Player]]:
        """Return supported player classes for the game."""
        ...

    def get_renderers(self, requirements: Callable[[Any], bool]) -> set[type[View]]:
        """Return supported view classes for the game."""
        ...

    def generate_rules(self, conf: Configuration) -> Rules:
        """Generate a rules instance from a game configuration."""
        ...

    # Each Game will be converted to a Singleton by SingletonFactory

class GameGovernor:
    """Singleton responsible for finding Game objects of each game available."""

    @classmethod
    def find_game(cls, name: str, requirement: Callable[[Any], bool], throw: bool = True) -> Game | None:
        """Find and return a registered game by name or alias."""
        ...

# endregion


# region playing

class PlayerIndex(int):
    """Primitive wrapper representing a player identifier in an arena."""

class Player(Recognizable, ABC):
    """Abstract player capable of selecting movements during a match."""

    @abstractmethod
    def play(self, pos: Position) -> Movement:
        """Choose and return the next movement for the given position."""
        ...

    @abstractmethod
    def starting_game(self, rules: Rules, player_index: PlayerIndex) -> None:
        """Initialize player state when a new game begins."""
        ...

class HumanPlayer(Player, ABC):
    """Abstract human player that delegates interaction to a view."""

    render: View

class PolyvalentTerminalPlayer(HumanPlayer):
    """Generic terminal human player driven by indexed movement selection for any game."""

class PolyvalentRandomPlayer(Player):
    """Generic player that selects movements uniformly at random for any game."""

    rng: RandomGenerator

# endregion


# region scoring

class Score(float):
    """Primitive wrapper for a score value where higher is better."""

class ScoreBoard:
    """Container for per-player scores at a given position."""

    def get_score(self, index: PlayerIndex) -> Score:
        """Return the score of the requested player index."""
        ...

# endregion


# region arening

class Arena(ABC):

    @abstractmethod
    def play(self, rules: Rules, players: List[Player], view: View) -> ScoreBoard:
        """Play a match between players under the given rules and return the final scoreboard."""
        ...

class ArenaFactory:

    @classmethod
    def create_arena(
            cls,
            rules: Rules,
            view: View,
            players: Sequence[Player],
            max_turns: int,
            max_turn_time_s: float,
            max_total_time_s: float,
            score_limits: Tuple[Score, Score],
            store_logs: bool
        ) -> Arena:
        """Return a compatible arena instance for the given rules."""
        ...

class GenericArena(Arena, ABC):

    @abstractmethod
    def _execute_turn(self) -> None:
        """Execute one turn of the game and return the resulting position."""
        ...

    @abstractmethod
    def _check_timeout(self) -> bool:
        """Check if the elapsed time exceeds the given timeout threshold."""
        ...

    @abstractmethod
    def _check_score_limit(self) -> bool:
        """Check if any player's score has reached the specified limit."""
        ...

    @abstractmethod
    def _check_max_turns(self) -> bool:
        """Check if the turn count has reached the maximum allowed turns."""
        ...

    @abstractmethod
    def _store_logs(self, last_movement: Movement) -> None:
        """Store the collected movement and/or current position."""
        ...

    def _game_loop(self) -> ScoreBoard:
        """Run the main game loop until a termination condition is met."""
        ...

# endregion


# region visualizing

class Canvas(ABC):
    """Abstract canvas surface used by views to render output."""

class View(ABC):
    """Abstract view responsible for rendering state and handling input."""

    players: List[Player]

    @abstractmethod
    def render_info(self, rules: Rules, canvas: Canvas) -> None:
        """Render static or contextual game information into a canvas."""
        ...

    @abstractmethod
    def render_state(self, pos: Position, canvas: Canvas) -> None:
        """Render the current game position into a canvas."""
        ...

    @abstractmethod
    def capture_input(self, *args: Any) -> Movement:
        """Capture user input and convert it to a movement."""
        ...

class EmptyView(View):
    """No-op view used when rendering and input capture are unnecessary."""

    def render_info(self, rules: Rules, canvas: Canvas) -> None:
        """Render no-op information for non-visual games."""
        ...

    def render_state(self, pos: Position, canvas: Canvas) -> None:
        """Render no-op state for non-visual games."""
        ...

    def capture_input(self, *args: Any) -> Movement:
        """Capture no-op input for non-interactive games."""
        ...

# endregion


# region visualizing.terminal_frontend

class TerminalView(View, ABC):
    """Abstract terminal frontend contract for game-specific terminal views.
    A new game would inherit from this view to be played as a terminal game.
    """

    input_fnc: Any = input
    output_fnc: Any = print

    def render_info(self, rules: Rules, canvas: Canvas) -> None:
        """Render terminal info layer using default terminal frontend behavior."""
        ...

    def render_state(self, pos: Position, canvas: Canvas) -> None:
        """Render terminal state layer using default terminal frontend behavior."""
        ...

    @abstractmethod
    def get_str_info(self, rules: Rules) -> str:
        """Return the formatted info text representation for terminal output."""
        ...

    @abstractmethod
    def get_str_state(self, position: Position) -> str:
        """Return the formatted state text representation for terminal output."""
        ...

    @abstractmethod
    def capture_input(self, input: str) -> Movement:
        """Convert a terminal input string into a movement."""
        ...

# endregion


# region visualizing.streamlit_frontend

class StreamlitContainer:
    """Placeholder streamlit container type used by the architecture skeleton."""

class StreamlitSession:
    """Placeholder streamlit session type used by the architecture skeleton."""

class StreamlitView(View, ABC):
    """Abstract streamlit frontend contract for game-specific streamlit views.
    A new game would inherit from this view to be played as a streamlit game.
    """

    @abstractmethod
    def render_info(self, rules: Rules, canvas: Canvas) -> None:
        """Render streamlit info layer with app-specific widgets."""
        ...

    def render_state(self, pos: Position, canvas: Canvas) -> None:
        """Render streamlit state layer using default frontend behavior."""
        ...

    @abstractmethod
    def render_position(self, position: Position, canvas: StreamlitContainer) -> None:
        """Render the current position section in streamlit."""
        ...

    @abstractmethod
    def render_movements(self, position: Position, canvas: StreamlitContainer) -> None:
        """Render available movements section in streamlit."""
        ...

    @abstractmethod
    def render_score(self, position: Position, canvas: StreamlitContainer) -> None:
        """Render available movements section in streamlit."""
        ...

    @abstractmethod
    def capture_input(self, state: StreamlitSession) -> Movement:
        """Capture streamlit UI state and convert it into a movement."""
        ...

# endregion


# region grading

class DebugLevel(Enum):
    """Debug level for trial execution with increasing verbosity."""
    NONE = 0
    ERROR = 1
    WARNING = 2
    USER = 3
    INFO = 4
    DEBUG = 5

@dataclass
class MatchConfiguration:
    """Generic match execution limits shared across game trials."""

    move_timeout_s: float
    total_timeout_s: float
    max_turns: int
    score_limits: Tuple[Score, Score]

@dataclass
class TrialConfiguration:
    """Configuration for a trial consisting of repeated matches under the same setup."""

    match_configuration: MatchConfiguration
    trialing_player_index: PlayerIndex
    rules: Rules
    players: List[Player]
    repetitions: int
    allow_fails: int

class MatchReport:
    """Result snapshot of a single match execution."""

    moves: int
    total_time_s: float
    score: Score
    messages: Map

class Trial:
    """Trial runner that evaluates one player setup over repeated matches."""
    configuration: TrialConfiguration
    match_reports: List[MatchReport]

    def trial(self, debug_level: DebugLevel = DebugLevel.USER) -> List[MatchReport]:
        """Run match repetitions and return generated reports."""
        ...

    def score(self) -> float:
        """Compute the aggregated numeric score for the trial."""
        ...

class Exam:
    """Collection of trials used to grade one player over a suite."""

    game: Game
    player: Player
    suite_configuration: ConfigurationSuite
    trials: List[Trial]
    trial_value: List[float]

    def grade(self, debug_level: DebugLevel = DebugLevel.USER) -> List[List[MatchReport]]:
        """Execute all trials and return nested match reports."""
        ...

    def score(self) -> float:
        """Compute the final numeric score across all trials."""
        ...

class AutoGrader:
    """Facade that bridges user configuration files with exam grading."""

    grader: Exam
    configuration_file: str
    player_file: str

    def grade(self) -> List[List[MatchReport]]:
        """Run grading and return grouped match reports."""
        ...

    def score(self) -> float:
        """Return the final numeric score computed by the grader."""
        ...

# endregion


# region apps.terminal

class TerminalApp:
    """Terminal executable orchestrating game setup and gameplay loop."""

    arena: Arena
    view: TerminalView

    def ask_for_game(self) -> Game:
        """Request and return the selected game from terminal input."""
        ...

    def ask_for_configuration(self) -> Configuration:
        """Request and return the selected game configuration."""
        ...

    def ask_for_player(self) -> Player:
        """Request and return the selected player configuration."""
        ...

    def run(self) -> None:
        """Run the terminal application entrypoint flow."""
        ...

    def main(self) -> None:
        """This object is an executable."""
        ...

# endregion


# region apps.streamlit

class ConfigurationPanel:
    """Streamlit panel responsible for player and configuration selection."""

    controls: Any

    def ask_for_player(self) -> Player:
        """Return the selected player from panel controls."""
        ...

    def ask_for_configuration(self) -> Configuration:
        """Return the selected configuration from panel controls."""
        ...

class MovementPanel:
    """Streamlit panel dedicated to movement interaction widgets."""

class StatePanel:
    """Streamlit panel dedicated to current game state rendering."""

class MainApp:
    """Main streamlit layout holder wiring all UI panels together."""

    left_column: ConfigurationPanel
    right_column: MovementPanel
    central: StatePanel

class StreamlitApp:
    """Streamlit executable orchestrating game selection and UI rendering."""

    main_app: MainApp
    view: StreamlitView

    def ask_for_game(self) -> Configuration:
        """Request and return the selected game from streamlit UI."""
        ...

    def main(self) -> None:
        """Run the streamlit application entrypoint flow."""
        ...

# endregion


# region gaming.Hanoi

class HanoiPosition(Position):
    """Concrete Hanoi position containing peg state and step counter."""

    n_pegs: int
    disks: List[int]
    steps: int

class HanoiMovement(Movement):
    """Concrete Hanoi movement defining source and destination pegs."""

    from_peg: int
    to_peg: int

class HanoiConfiguration(Configuration):
    """Concrete Hanoi configuration defining initial disk-to-peg layout."""

    n_pegs: int
    disks: List[int]

class HanoiRules(Rules):
    """Concrete rules implementation for the Hanoi game."""

class HanoiGame(Game):
    """Concrete game registry implementation for Hanoi."""

class HanoiOracle(Oracle):
    """Concrete benchmark oracle implementation for Hanoi."""

class HanoiPerfectPlayer(Player):
    """Concrete player implementation that uses the optimal Hanoi solution strategy."""

class HanoiTerminalView(TerminalView):
    """Concrete terminal view implementation for the Hanoi game."""

class HanoiStreamlitView(StreamlitView):
    """Concrete streamlit view implementation for the Hanoi game."""

# endregion
