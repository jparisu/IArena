# SquareMap Documentation

This document explains how to **create**, **inspect**, **navigate**, and **generate** `SquareMap` objects using the provided square-grid mapping utilities.

The main components are:

- `SquareMapCoordinate`: represents one position in the grid.
- `SquareMapDirection`: represents one cardinal direction.
- `SquareMap[T]`: stores the rectangular grid itself.
- `AbstractMapGenerator`: defines the interface for map generators.
- `MapFactory`: provides a registry-based entrypoint to generate maps with different strategies.

---

# 1. Overview

A `SquareMap` is a rectangular grid indexed by `SquareMapCoordinate`. It supports:

- bounds checking,
- coordinate iteration,
- neighbor and direction queries,
- numeric helpers for float-based maps,
- conversion to and from NumPy arrays.

This makes it suitable for pathfinding, board games, terrain generation, and any grid-based environment.

---

# 2. Core Types

## 2.1 `SquareMapCoordinate`

`SquareMapCoordinate` represents a grid location with two integer attributes:

- `x`: row index
- `y`: column index

It also provides helper methods to move to neighboring coordinates and compute Manhattan distance.

### Main methods

- `from_tuple((x, y))`
- `up()`
- `down()`
- `left()`
- `right()`
- `moved(direction)`
- `from_direction(direction)`
- `manhattan_distance(other)`
- `as_tuple()`
- `neighbors()`

### Example

```python
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.SquareMapDirection import SquareMapDirection

coord = SquareMapCoordinate(2, 3)

print(coord.as_tuple())                     # (2, 3)
print(coord.up())                           # SquareMapCoordinate(1, 3)
print(coord.right())                        # SquareMapCoordinate(2, 4)
print(coord.moved(SquareMapDirection.LEFT)) # SquareMapCoordinate(2, 2)

other = SquareMapCoordinate(5, 1)
print(coord.manhattan_distance(other))      # 5

print("Neighbors:")
for direction, neighbor in coord.neighbors():
    print(direction, neighbor)
```

Why it matters:

`SquareMapCoordinate` is the standard way to refer to locations in the framework. Using this class instead of raw tuples makes navigation and neighbor operations clearer and safer.

---

## 2.2 `SquareMapDirection`

`SquareMapDirection` is an enum with the four cardinal directions:

- `UP = (-1, 0)`
- `RIGHT = (0, 1)`
- `DOWN = (1, 0)`
- `LEFT = (0, -1)`

### Main features

- `delta`: returns the `(dx, dy)` associated with the direction.
- `opposite()`: returns the opposite direction.

### Example

```python
from iarena.utilizing.mapping.square_map.SquareMapDirection import SquareMapDirection

direction = SquareMapDirection.RIGHT

print(direction.delta)      # (0, 1)
print(direction.opposite()) # SquareMapDirection.LEFT
```

Why it matters:

Directions are the formal movement language for square maps. They are used by coordinates, maps, and games to describe navigation consistently.

---

## 2.3 `SquareMap[T]`

`SquareMap` is the rectangular grid container. It accepts any rectangular iterable of iterables and stores it internally as a list of lists.

### Construction rules

A valid map must:

- contain at least one row,
- contain at least one column,
- be rectangular, meaning all rows must have the same length.

### Example

```python
from iarena.utilizing.mapping.square_map.SquareMap import SquareMap
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate

grid = SquareMap([
    [1.0, 2.0, 3.0],
    [4.0, 5.0, 6.0],
    [7.0, 8.0, 9.0],
])

print(grid)
print(grid.pretty_text())
print(grid.size())      # (3, 3)
print(grid.n_rows())    # 3
print(grid.n_cols())    # 3

coord = SquareMapCoordinate(1, 1)
print(grid[coord])      # 5.0

grid[coord] = 10.0
print(grid[coord])      # 10.0
```

Why it matters:

`SquareMap` is the central data structure for storing square-grid environments. It provides both container behavior and navigation-aware helper methods.

---

# 3. Working with a `SquareMap`

## 3.1 Bounds checking

The map provides several ways to check whether a coordinate is valid.

### Methods

- `in_bounds(coord) -> bool`
- `require_in_bounds(coord)`
- `get(coord, default=None)`

### Example

```python
from iarena.utilizing.mapping.square_map.SquareMap import SquareMap
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate

grid = SquareMap([
    [1, 2],
    [3, 4],
])

inside = SquareMapCoordinate(1, 1)
outside = SquareMapCoordinate(3, 0)

print(grid.in_bounds(inside))   # True
print(grid.in_bounds(outside))  # False
print(grid.get(inside))         # 4
print(grid.get(outside, -1))    # -1
```

Why it matters:

Most grid algorithms depend on careful boundary handling. These methods make it easy to validate positions safely.

---

## 3.2 Neighbor and direction queries

`SquareMap` can compute valid neighbors and valid directions from a coordinate, automatically filtering out out-of-bounds moves.

### Methods

- `possible_direction_neighbors(coord)`
- `possible_directions(coord)`
- `possible_neighbors(coord)`

### Example

```python
from iarena.utilizing.mapping.square_map.SquareMap import SquareMap
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate

grid = SquareMap([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
])

coord = SquareMapCoordinate(0, 0)

print("Possible directions:")
for direction in grid.possible_directions(coord):
    print(direction)

print("Possible neighbors:")
for neighbor in grid.possible_neighbors(coord):
    print(neighbor)

print("Direction-neighbor pairs:")
for direction, neighbor in grid.possible_direction_neighbors(coord):
    print(direction, neighbor)
```

Why it matters:

These methods are useful for search, movement validation, pathfinding, and game rules.

---

## 3.3 Iteration helpers

You can iterate over all coordinates and all values in a map.

### Methods

- `iter_coordinates()`
- `iter_values()`

### Example

```python
from iarena.utilizing.mapping.square_map.SquareMap import SquareMap

grid = SquareMap([
    [1, 2],
    [3, 4],
])

print("Coordinates:")
for coord in grid.iter_coordinates():
    print(coord)

print("Values:")
for value in grid.iter_values():
    print(value)
```

Why it matters:

These helpers are convenient for analysis, transformations, statistics, and debugging.

---

## 3.4 Numeric helpers

For numeric maps, `SquareMap` provides aggregate helpers.

### Methods

- `min()`
- `max()`
- `sum()`
- `check(allow_zero=True, skip_coordinate_validation=None)`

### Example

```python
from iarena.utilizing.mapping.square_map.SquareMap import SquareMap
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate

grid = SquareMap([
    [1.0, 2.0],
    [3.0, 4.0],
])

print(grid.min())   # 1.0
print(grid.max())   # 4.0
print(grid.sum())   # 10.0

grid.check()

grid_with_zero = SquareMap([
    [1.0, 0.0],
    [2.0, 3.0],
])

grid_with_zero.check(allow_zero=True)

try:
    grid_with_zero.check(allow_zero=False)
except ValueError as exc:
    print(exc)

grid_with_zero.check(
    allow_zero=False,
    skip_coordinate_validation=[SquareMapCoordinate(0, 1)]
)
```

Why it matters:

These methods are especially relevant for cost maps, where negative or zero values may or may not be allowed depending on the use case.

---

## 3.5 NumPy conversion and copying

`SquareMap` supports conversion to and from NumPy arrays.

### Methods

- `from_numpy(array)`
- `to_numpy(dtype=float)`
- `copy()`

### Example

```python
import numpy as np

from iarena.utilizing.mapping.square_map.SquareMap import SquareMap

array = np.array([
    [1.0, 2.0],
    [3.0, 4.0],
])

grid = SquareMap.from_numpy(array)
print(grid.pretty_text())

back_to_numpy = grid.to_numpy()
print(back_to_numpy)

grid_copy = grid.copy()
print(grid_copy.pretty_text())
```

Why it matters:

NumPy conversion is useful when integrating square maps with scientific code, generators, or visualization tools.

---

## 3.6 Convenience constructors

`SquareMap` also provides utility constructors.

### Methods

- `full(n_rows, n_cols, value)`
- `zeros(n_rows, n_cols)`
- `zeros_like(smap)`

### Example

```python
from iarena.utilizing.mapping.square_map.SquareMap import SquareMap

full_map = SquareMap.full(3, 4, 7)
print(full_map.pretty_text())

zero_map = SquareMap.zeros(2, 3)
print(zero_map.pretty_text())

zero_like = SquareMap.zeros_like(full_map)
print(zero_like.pretty_text())
```

Why it matters:

These constructors are useful when initializing empty states, masks, heuristic maps, or default-cost grids.

---

## 3.7 Compass direction

`SquareMap` can estimate the dominant cardinal direction between two coordinates.

### Method

- `compass_direction(from_coord, to_coord, fail_on_same=True)`

### Example

```python
from iarena.utilizing.mapping.square_map.SquareMap import SquareMap
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate

grid = SquareMap.full(5, 5, 1.0)

origin = SquareMapCoordinate(1, 1)
target = SquareMapCoordinate(4, 2)

print(grid.compass_direction(origin, target))
```

Behavior:

- if vertical distance dominates, the result is `UP` or `DOWN`,
- otherwise, the result is `LEFT` or `RIGHT`,
- if both coordinates are the same and `fail_on_same=True`, a `ValueError` is raised.

Why it matters:

This is useful for guidance systems, heuristics, and directional hints in games such as GoldMine.

---

# 4. Generating SquareMaps

## 4.1 Generator architecture

All map generators inherit from `AbstractMapGenerator`. Each generator exposes a class method:

```python
generate(n, m, start, target, rng, **kwargs) -> np.ndarray
```

The abstract base class also provides reusable validation and helper methods:

- dimension validation,
- coordinate validation,
- probability validation,
- random uniform and exponential sampling,
- path existence checking,
- Manhattan path carving,
- high-cost tile placement.

This design allows each generator to focus on one terrain-generation strategy while sharing common validation logic.

---

## 4.2 `MapFactory`

`MapFactory` is the main entrypoint for generation. It stores a registry of named generator strategies and exposes three important methods:

- `generate(...)`
- `register(name, generator)`
- `available_generation_methods()`

### Built-in methods

The provided registry includes:

- `empty`
- `uniform`
- `bimodel`
- `column`
- `exponential`
- `jumping`
- `perlin`

### Example

```python
from iarena.utilizing.mapping.square_map.SquareMap import SquareMap
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.generators.MapFactory import MapFactory
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator

start = SquareMapCoordinate(0, 0)
target = SquareMapCoordinate(4, 4)
rng = RandomGenerator(seed=0)

generated = MapFactory.generate(
    name="uniform",
    n=5,
    m=5,
    start=start,
    target=target,
    rng=rng,
    integer=False,
    low=1.0,
    high=3.0,
)

grid = SquareMap.from_numpy(generated)

print(MapFactory.available_generation_methods())
print(grid.pretty_text())
```

Why it matters:

`MapFactory` makes generation consistent and extensible. Client code can choose a method by name without depending directly on each generator class.

---

# 5. Built-in Generation Methods

## 5.1 `EmptyMap`

Returns a fully walkable grid filled with a constant cost.

### Parameters

- `cost` (default: `1.0`)

### Example

```python
generated = MapFactory.generate(
    name="empty",
    n=4,
    m=4,
    start=start,
    target=target,
    rng=rng,
    cost=1.0,
)
```

Use case:

Best for debugging, deterministic baselines, and maps where all tiles should have the same traversal cost.

---

## 5.2 `UniformMap`

Samples every tile independently from a uniform distribution.

### Parameters

- `low` (default: `1.0`)
- `high` (default: `2.0`)

### Example

```python
generated = MapFactory.generate(
    name="uniform",
    n=4,
    m=4,
    start=start,
    target=target,
    rng=rng,
    low=1.0,
    high=5.0,
)
```

Use case:

Useful for generic random cost landscapes without strong structure.

---

## 5.3 `ExponentialMap`

Samples costs from an exponential distribution and shifts them by `1.0`.

### Parameters

- `scale` (default: `1.0`)

### Example

```python
generated = MapFactory.generate(
    name="exponential",
    n=4,
    m=4,
    start=start,
    target=target,
    rng=rng,
    scale=2.0,
)
```

Use case:

Useful when most tiles should be relatively cheap but some rare tiles should be much more expensive.

---

## 5.4 `PerlinMap`

Creates a smooth Perlin-like terrain using structured noise.

### Parameters

- `low` (default: `1.0`)
- `high` (default: `10.0`)

### Example

```python
generated = MapFactory.generate(
    name="perlin",
    n=8,
    m=8,
    start=start,
    target=target,
    rng=rng,
    low=1.0,
    high=8.0,
)
```

Use case:

Useful for terrain-like maps where neighboring cells should have correlated values instead of independent noise.

---

## 5.5 `BimodelMap`

Creates a map with two terrain states: low-cost and high-cost.

### Parameters

- `p_high` (default: `0.3`)
- `low_cost` (default: `1.0`)
- `high_cost` (default: `10.0`)

### Example

```python
generated = MapFactory.generate(
    name="bimodel",
    n=5,
    m=5,
    start=start,
    target=target,
    rng=rng,
    p_high=0.25,
    low_cost=1.0,
    high_cost=9.0,
)
```

Use case:

Useful when you want a simple discrete distinction between easy and difficult terrain.

---

## 5.6 `JumpingMap`

Starts from a grid of ones and randomly inserts high-cost tiles while preserving walkable endpoints.

### Parameters

- `p` (default: `0.2`)
- `high_cost` (default: `10.0`)

### Example

```python
generated = MapFactory.generate(
    name="jumping",
    n=5,
    m=5,
    start=start,
    target=target,
    rng=rng,
    p=0.3,
    high_cost=12.0,
)
```

Use case:

Useful for sparse hazard-style maps where most cells are cheap but some are sharply more expensive.

---

## 5.7 `ColumnMap`

Generates a map of ones and zeros, possibly blocking cells, while guaranteeing a path between start and target.

### Parameters

- `p_block` or `p` (default: `0.35`)

### Example

```python
generated = MapFactory.generate(
    name="column",
    n=6,
    m=6,
    start=start,
    target=target,
    rng=rng,
    p_block=0.4,
)
```

Use case:

Useful for obstacle maps or connectivity-based experiments where blocked cells are represented by `0.0`.

Important note:

If the initial random blocking breaks connectivity, the generator automatically carves a Manhattan path from start to target.

---

# 6. Integer vs Float generation

`MapFactory.generate(...)` includes an `integer` flag.

- if `integer=False`, the generated grid is returned as `float`,
- if `integer=True`, the generated values are rounded and converted to integers.

### Example

```python
generated = MapFactory.generate(
    name="uniform",
    n=4,
    m=4,
    start=start,
    target=target,
    rng=rng,
    integer=True,
    low=1.0,
    high=5.0,
)

print(generated)
print(generated.dtype)
```

Why it matters:

Some games or experiments require exact integer costs, while others benefit from continuous float values.

---

# 7. Registering a custom generator

You can extend the factory by registering a new class that inherits from `AbstractMapGenerator`.

### Example

```python
import numpy as np

from iarena.utilizing.mapping.square_map.generators.AbstractMapGenerator import AbstractMapGenerator
from iarena.utilizing.mapping.square_map.generators.MapFactory import MapFactory

class ConstantSevenMap(AbstractMapGenerator):
    @classmethod
    def generate(cls, n, m, start, target, rng, **kwargs):
        cls._validate_dims(n, m)
        cls._validate_coordinate(n, m, start, "start")
        cls._validate_coordinate(n, m, target, "target")
        return np.full((n, m), 7.0, dtype=float)

MapFactory.register("constant7", ConstantSevenMap)

print(MapFactory.available_generation_methods())
```

Why it matters:

This makes the map-generation system extensible without changing the existing factory or built-in generators.

---

# 8. Complete example

The following example builds a generated map, wraps it in `SquareMap`, and inspects it.

```python
from iarena.utilizing.mapping.square_map.SquareMap import SquareMap
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.generators.MapFactory import MapFactory
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator

start = SquareMapCoordinate(0, 0)
target = SquareMapCoordinate(5, 5)
rng = RandomGenerator(seed=42)

generated = MapFactory.generate(
    name="bimodel",
    n=6,
    m=6,
    start=start,
    target=target,
    rng=rng,
    p_high=0.3,
    low_cost=1.0,
    high_cost=8.0,
)

grid = SquareMap.from_numpy(generated)

print("Generated map:")
print(grid.pretty_text())

print("Map size:", grid.size())
print("Min cost:", grid.min())
print("Max cost:", grid.max())
print("Sum:", grid.sum())

print("Possible directions from start:")
for direction in grid.possible_directions(start):
    print(direction)
```

---

# 9. Recommended workflow

A practical workflow for using square maps is:

1. define `start` and `target` as `SquareMapCoordinate`,
2. generate a NumPy grid with `MapFactory.generate(...)` or build one manually,
3. wrap the grid in `SquareMap`,
4. use map methods to inspect coordinates, neighbors, and values,
5. validate the map with `check(...)` if the map is cost-based,
6. integrate the map into a game, environment, or search algorithm.

This workflow keeps generation, storage, validation, and navigation clearly separated.

---

# 10. Summary

The square-map utilities provide a compact but flexible toolkit for working with rectangular grids:

- `SquareMapCoordinate` models positions,
- `SquareMapDirection` models movement directions,
- `SquareMap` stores and manipulates the grid,
- `AbstractMapGenerator` defines reusable generator structure,
- `MapFactory` exposes named generation strategies.

Together, they support both manually defined maps and procedurally generated maps, making them suitable for tutorials, debugging, experiments, and full game implementations.
