
from typing import Dict, Iterator, List, Tuple
from enum import Enum
from queue import PriorityQueue
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

from IArena.interfaces.IMovement import IMovement
from IArena.utils.printing import matrix_map_to_str
from IArena.utils.RandomGenerator import RandomGenerator



class SquareMapMovement(IMovement):
    """
    Represents the movement of the player in the grid.

    Values:
        Up: 0 - Move up.
        Down: 1 - Move down.
        Left: 2 - Move left.
        Right: 3 - Move right.
    """

    class Direction(Enum):
        Up = 0
        Down = 1
        Left = 2
        Right = 3

    def __init__(
            self,
            direction: Direction):
        self.direction = direction

    def __eq__(
            self,
            other: "SquareMapMovement"):
        return self.direction == other.direction

    def __str__(self):
        return f'{{{self.direction.name}}}'

    @staticmethod
    def up() -> "SquareMapMovement":
        return SquareMapMovement(SquareMapMovement.Direction.Up)

    @staticmethod
    def down() -> "SquareMapMovement":
        return SquareMapMovement(SquareMapMovement.Direction.Down)

    @staticmethod
    def left() -> "SquareMapMovement":
        return SquareMapMovement(SquareMapMovement.Direction.Left)

    @staticmethod
    def right() -> "SquareMapMovement":
        return SquareMapMovement(SquareMapMovement.Direction.Right)



class SquareMapCoordinate:
    """
    Represents the coordinates of a square in the grid.

    Attributes:
        x: int - The x coordinate of the square.
        y: int - The y coordinate of the square.
    """

    def __init__(
            self,
            x: int,
            y: int):
        self.x = x
        self.y = y

    def __eq__(
            self,
            other: "SquareMapCoordinate"):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f'({self.x},{self.y})'

    def as_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)

    def __getitem__(self, index: int):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError(f"Index {index} out of range for SquareMapCoordinate. Allowed values: 0 or 1")

    def __hash__(self):
        return hash((self.x, self.y))

    # Comparison operator
    def __lt__(self, other: "SquareMapCoordinate"):
        if self.x == other.x:
            return self.y < other.y
        return self.x < other.x


class SquareMap:
    """
    Represents the grid of the game.

    Attributes:
        map: List[List[bool]] - The grid represented as a matrix of booleans.
                                   True represents a free square, and False represents a wall/obstacle.
    """

    def __init__(
            self,
            map: List[List[bool]]):
        self.map_ = map

    def __str__(self):
        # Convert to a matrix of spaces and X
        squares = [[' ' if cell else 'X' for cell in row] for row in self.map_]
        return matrix_map_to_str(squares)

    def size(self) -> Tuple[int, int]:
        return len(self.map_), len(self.map_[0]) if self.map_ else 0

    def __len__(self):
        return len(self.map_)

    def __getitem__(self, index: Tuple[int, int]):
        i, j = index
        return self.map_[i][j]

    def in_bounds(self, coord: SquareMapCoordinate) -> bool:
        rows, cols = self.size()
        return 0 <= coord.x < rows and 0 <= coord.y < cols

    def is_free(self, coord: SquareMapCoordinate) -> bool:
        return self.in_bounds(coord) and self.map_[coord.x][coord.y]

    def plot_2d_map(
                self,
                coordinates: Dict[str, SquareMapCoordinate] = {}
            ):

        rows, cols = self.size()
        grid = np.zeros((rows, cols))
        for i in range(rows):
            for j in range(cols):
                if not self.map_[i][j]:
                    grid[i, j] = 1
        plt.imshow(grid, cmap='Greys', origin='upper')
        for label, coord in coordinates.items():
            plt.scatter(coord.y, coord.x, s=100, label=label)
            plt.legend()
        plt.show()

def minimum_path(
        map: SquareMap,
        start: SquareMapCoordinate,
        target: SquareMapCoordinate) -> int:

    rows, cols = map.size()
    directions = {
        SquareMapMovement.Direction.Up: (-1, 0),
        SquareMapMovement.Direction.Down: (1, 0),
        SquareMapMovement.Direction.Left: (0, -1),
        SquareMapMovement.Direction.Right: (0, 1)
    }
    pq = PriorityQueue()
    pq.put((0, start))
    visited = set()
    while not pq.empty():
        cost, current = pq.get()
        if current == target:
            return cost
        if current in visited:
            continue
        visited.add(current)
        for direction, (dx, dy) in directions.items():
            neighbor = SquareMapCoordinate(current.x + dx, current.y + dy)
            if (0 <= neighbor.x < rows and
                    0 <= neighbor.y < cols and
                    map[neighbor.x, neighbor.y] and
                    neighbor not in visited):
                pq.put((cost + 1, neighbor))

    return float('inf')



def square_map_generator(
        rows: int,
        cols: int,
        obstacle_prob: float,
        rng: RandomGenerator = RandomGenerator()) -> SquareMap:
    map = []
    for i in range(rows):
        row = []
        for j in range(cols):
            if rng.random() < obstacle_prob:
                row.append(False)  # Wall
            else:
                row.append(True)   # Free square
        map.append(row)
    return SquareMap(map)


def generate_random_non_loop_path(
            rows: int,
            cols: int,
            start: SquareMapCoordinate,
            target: SquareMapCoordinate,
            approx_path_length: int,
            rng: RandomGenerator = RandomGenerator()
        ) -> List[SquareMapCoordinate]:

    DIRS = [(0,1), (1,0), (0,-1), (-1,0)]  # right, down, left, up

    def in_bounds(u: Tuple[int,int]) -> bool:
        x, y = u
        return 0 <= x < rows and 0 <= y < cols

    def neighbours(u: Tuple[int,int]):
        x, y = u
        for dx, dy in DIRS:
            v = (x + dx, y + dy)
            if in_bounds(v):
                yield v

    def manhattan(a: Tuple[int,int], b: Tuple[int,int]) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def legal_moves(cur: Tuple[int,int], visited: set) -> List[Tuple[int,int]]:
        """Moves that keep the path induced: the new cell may touch only `cur` among visited."""
        out = []
        for u in neighbours(cur):
            if u in visited:
                continue
            ok = True
            for w in neighbours(u):
                if w != cur and w in visited:
                    ok = False
                    break
            if ok:
                out.append(u)
        return out

    def bfs_reaches_end(cur: Tuple[int,int], end: Tuple[int,int], visited: set) -> bool:
        """Conservative reachability check ignoring the induced constraint but not revisiting."""
        q = deque([cur])
        seen = {cur}
        blocked = visited - {cur}
        while q:
            u = q.popleft()
            if u == end:
                return True
            for v in neighbours(u):
                if v in blocked or v in seen:
                    continue
                seen.add(v)
                q.append(v)
        return False

    # Normalize inputs
    s = start.as_tuple()
    t = target.as_tuple()
    if not (in_bounds(s) and in_bounds(t)):
        return []
    # at least the Manhattan distance is necessary
    need = max(approx_path_length, manhattan(s, t))

    # Effort limits (tune as needed)
    MAX_RESTARTS = 1500
    STEP_CAP = 200000

    steps_used_total = 0

    def dfs(path: List[Tuple[int,int]], visited: set) -> List[Tuple[int,int]] | None:
        nonlocal steps_used_total
        steps_used_total += 1
        if steps_used_total > STEP_CAP:
            return None

        cur = path[-1]
        L = len(path) - 1  # number of edges so far

        if cur == t and L >= need:
            return path

        if not bfs_reaches_end(cur, t, visited):
            return None

        cands = legal_moves(cur, visited)
        # steer away from entering target too early
        if L < need - 1:
            cands = [u for u in cands if u != t]
        if not cands:
            return None

        # dead-end lookahead prune and gather mobility for scoring
        scored = []
        for u in cands:
            visited.add(u)
            nm = legal_moves(u, visited)
            visited.remove(u)
            if u == t and L + 1 >= need:
                scored.append((u, 1))
            elif nm:
                scored.append((u, len(nm)))
        if not scored:
            return None

        # heuristic ordering: before reaching `need`, prefer moves that increase distance (stretch);
        # afterwards, prefer those that decrease it; break ties by mobility and randomness.
        rng.shuffle(scored)
        if L < need:
            scored.sort(key=lambda p: (manhattan(p[0], t) - manhattan(cur, t), p[1]))
        else:
            scored.sort(key=lambda p: (manhattan(cur, t) - manhattan(p[0], t), p[1]))

        for u, _mob in reversed(scored):
            visited.add(u)
            path.append(u)
            out = dfs(path, visited)
            if out is not None:
                return out
            path.pop()
            visited.remove(u)
        return None

    # Multiple randomized restarts
    for _ in range(MAX_RESTARTS):
        rng.shuffle(DIRS)  # vary local geometry preference
        steps_used_total = 0
        path0 = [s]
        visited0 = {s}
        out = dfs(path0, visited0)
        if out is not None:
            # Convert back to SquareMapCoordinate
            return [SquareMapCoordinate(x, y) for x, y in out]

    return []


def square_valid_map_generator(
        rows: int,
        cols: int,
        start: SquareMapCoordinate,
        target: SquareMapCoordinate,
        approx_path_length: int,
        approx_obstacle_prob: float,
        rng: RandomGenerator = RandomGenerator()) -> SquareMap:

    map = square_map_generator(rows, cols, approx_obstacle_prob, rng)
    path = generate_random_non_loop_path(rows, cols, start, target, approx_path_length)
    for coord in path:
        map.map_[coord.x][coord.y] = True  # Ensure path is free
    map.map_[start.x][start.y] = True  # Ensure start is free
    map.map_[target.x][target.y] = True  # Ensure target is free
    return map
