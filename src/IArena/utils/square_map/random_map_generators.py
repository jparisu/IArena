from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from typing import Any, Dict, Protocol, Tuple, Type, List
import numpy as np

from IArena.utils.square_map.perlin_generator import perlin_generator
from IArena.utils.RandomGenerator import RandomGenerator
from IArena.utils.square_map.SquareMap import Coordinate


class AbstractMapGenerator(ABC):
    """
    Abstract base for non-instance map generators.

    Subclasses MUST implement:
        generate(n, m, start, target, rng, **kwargs) -> np.ndarray
    """

    @classmethod
    @abstractmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: Coordinate,
        target: Coordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> np.ndarray:
        raise NotImplementedError

    # ---------- Shared validation/helpers ----------
    @staticmethod
    def _validate_dims(n: int, m: int) -> None:
        if not (isinstance(n, int) and isinstance(m, int) and n > 0 and m > 0):
            raise ValueError("n and m must be positive integers.")

    @staticmethod
    def _validate_Coordinate(n: int, m: int, c: Coordinate, name: str) -> None:
        r, c2 = c
        if not (0 <= r < n and 0 <= c2 < m):
            raise ValueError(f"{name} must be inside the map. Got {c} for shape ({n},{m}).")

    @staticmethod
    def _validate_p(p: float) -> None:
        if not (0.0 <= p <= 1.0):
            raise ValueError("p must be in [0, 1].")

    @staticmethod
    def _uniform01(rng: RandomGenerator) -> float:
        """Uniform in [0,1) using your rng.rand()."""
        return rng.rand()

    @classmethod
    def _uniform(cls, rng: RandomGenerator, low: float, high: float) -> float:
        if hasattr(rng, "uniform"):
            return float(rng.uniform(low, high))  # type: ignore[attr-defined]
        return low + (high - low) * cls._uniform01(rng)

    @classmethod
    def _exponential(cls, rng: RandomGenerator, scale: float) -> float:
        if hasattr(rng, "exponential"):
            return float(rng.exponential(scale=scale))  # type: ignore[attr-defined]
        # Inverse CDF: X = -scale * ln(1-U)
        u = cls._uniform01(rng)
        u = min(max(u, 1e-15), 1.0 - 1e-15)
        return -scale * np.log(1.0 - u)

    @staticmethod
    def _has_path_4neigh(grid: np.ndarray, start: Coordinate, target: Coordinate) -> bool:
        """
        Path existence using 4-neighborhood through cost==1 tiles.
        """
        n, m = grid.shape
        sr, sc = start
        tr, tc = target

        if grid[sr, sc] != 1.0 or grid[tr, tc] != 1.0:
            return False

        q = deque([start])
        seen = np.zeros((n, m), dtype=bool)
        seen[sr, sc] = True

        while q:
            r, c = q.popleft()
            if (r, c) == target:
                return True

            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                rr, cc = r + dr, c + dc
                if 0 <= rr < n and 0 <= cc < m and not seen[rr, cc] and grid[rr, cc] == 1.0:
                    seen[rr, cc] = True
                    q.append((rr, cc))

        return False

    @staticmethod
    def _carve_manhattan_path(grid: np.ndarray, start: Coordinate, target: Coordinate) -> None:
        """
        Force a simple Manhattan path (cost=1) from start to target by setting tiles to 1.
        """
        r, c = start
        tr, tc = target

        step_r = 1 if tr > r else -1
        while r != tr:
            grid[r, c] = 1.0
            r += step_r

        step_c = 1 if tc > c else -1
        while c != tc:
            grid[r, c] = 1.0
            c += step_c

        grid[tr, tc] = 1.0


    @staticmethod
    def _ensure_random_path_by_digging(
        grid: np.ndarray,
        start: Coordinate,
        target: Coordinate,
        rng,
        high_cost: float,
        *,
        max_steps: int | None = None,
    ) -> np.ndarray:
        """
        Ensures a path of cost==1 exists from start to target by repeatedly turning a random
        high_cost tile into 1.0 until connectivity is achieved.

        - The resulting path is not forced to be Manhattan/linear; it emerges randomly depending
        on which tiles were flipped.
        - This mutates `grid` in-place and also returns it.

        Parameters
        ----------
        grid:
            2D float array.
        start, target:
            Coordinates (row, col). Must be in-bounds.
        rng:
            Your RandomGenerator (must have randint(high, low=0)).
        high_cost:
            The value considered "blocked" / "high". Only tiles equal to this value will be flipped.
        max_steps:
            Optional safety cap. If None, will flip at most all high_cost tiles.

        Behavior
        --------
        - If path already exists, does nothing.
        - Otherwise:
            while no path:
                pick a random high_cost tile (uniformly among all remaining high_cost tiles)
                set it to 1.0
        - If it runs out of high_cost tiles before a path exists, raises RuntimeError.
        """
        n, m = grid.shape

        def _in_bounds(c: Coordinate) -> bool:
            r, c2 = c
            return 0 <= r < n and 0 <= c2 < m

        if not _in_bounds(start) or not _in_bounds(target):
            raise ValueError("start and target must be inside grid bounds.")

        # Ensure endpoints are traversable
        grid[start] = 1.0
        grid[target] = 1.0

        if AbstractMapGenerator._has_path_4neigh(grid, start, target):
            return grid

        # Collect Coordinates of all high tiles
        high_positions = np.argwhere(grid == high_cost)
        if high_positions.size == 0:
            raise RuntimeError("No high_cost tiles available to flip, but no path exists.")

        # Steps bound: flip at most all highs unless user sets a smaller cap
        if max_steps is None:
            max_steps = high_positions.shape[0]
        else:
            max_steps = int(max_steps)
            if max_steps <= 0:
                raise ValueError("max_steps must be > 0 or None.")

        # We want to sample without replacement efficiently.
        # We'll keep a list of remaining high tiles and remove by swap-pop.
        remaining = high_positions.tolist()  # list of [r, c]
        steps = 0

        while steps < max_steps:
            if not remaining:
                break

            # pick random index in [0, len(remaining)-1]
            idx = rng.randint(high=len(remaining), low=0)
            r, c = remaining[idx]

            # flip it
            grid[r, c] = 1.0
            steps += 1

            # remove this position from remaining (swap with last then pop)
            remaining[idx] = remaining[-1]
            remaining.pop()

            if AbstractMapGenerator._has_path_4neigh(grid, start, target):
                return grid

        raise RuntimeError(
            "Failed to ensure a path within max_steps. "
            "Either increase max_steps or reduce obstacle density."
        )

    @classmethod
    def _set_random_high_tiles(
        cls,
        grid: np.ndarray,
        rng: RandomGenerator,
        p: float,
        high_cost: float,
        avoid: Tuple[Coordinate, Coordinate] | None = None,
    ) -> None:
        """
        Set a fraction p of *tiles* to high_cost (uniformly sampled without replacement),
        optionally avoiding two Coordinates (start/target).

        Mutates grid in-place.
        """
        n, m = grid.shape
        total = n * m
        k = int(round(p * total))

        if k <= 0:
            return

        # Build list of candidate linear indices
        if avoid is None:
            candidates = np.arange(total, dtype=int)
        else:
            (sr, sc), (tr, tc) = avoid
            avoid_set = {sr * m + sc, tr * m + tc}
            candidates = np.array([idx for idx in range(total) if idx not in avoid_set], dtype=int)

        if k >= candidates.size:
            # set everything available to high cost
            rr, cc = np.unravel_index(candidates, (n, m))
            grid[rr, cc] = high_cost
            return

        # Sample k unique indices from candidates using Fisher-Yates partial shuffle
        # on the candidates array itself.
        cand = candidates.copy()
        for i in range(k):
            j = rng.randint(high=cand.size, low=i)
            cand[i], cand[j] = cand[j], cand[i]

        chosen = cand[:k]
        rr, cc = np.unravel_index(chosen, (n, m))
        grid[rr, cc] = high_cost


# ---------------- Concrete generators ----------------

class EmptyMap(AbstractMapGenerator):
    @classmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: Coordinate,
        target: Coordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> np.ndarray:
        cls._validate_dims(n, m)
        cls._validate_Coordinate(n, m, start, "start")
        cls._validate_Coordinate(n, m, target, "target")
        return np.ones((n, m), dtype=float)


class BimodelMap(AbstractMapGenerator):
    """
    All tiles cost 1, and a fraction p of random tiles cost (n*m + 1).

    kwargs:
      - p: float in [0,1] (required)
    """

    @classmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: Coordinate,
        target: Coordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> np.ndarray:
        cls._validate_dims(n, m)
        cls._validate_Coordinate(n, m, start, "start")
        cls._validate_Coordinate(n, m, target, "target")

        p = float(kwargs.get("p", 0.4))
        cls._validate_p(p)

        grid = np.ones((n, m), dtype=float)
        high_cost = float(n * m + 1)

        cls._set_random_high_tiles(grid, rng=rng, p=p, high_cost=high_cost, avoid=None)
        return grid


class JumpingMap(AbstractMapGenerator):
    """
    Like BimodelMap, but ensures start and target are cost-1.

    kwargs:
      - p: float in [0,1] (required)
    """

    @classmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: Coordinate,
        target: Coordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> np.ndarray:
        cls._validate_dims(n, m)
        cls._validate_Coordinate(n, m, start, "start")
        cls._validate_Coordinate(n, m, target, "target")

        p = float(kwargs.get("p", 0.4))
        cls._validate_p(p)

        grid = np.ones((n, m), dtype=float)
        high_cost = float(n * m + 1)

        cls._set_random_high_tiles(grid, rng=rng, p=p, high_cost=high_cost, avoid=(start, target))
        grid[start.as_tuple()] = 1.0
        grid[target.as_tuple()] = 1.0
        return grid


class ColumnMap(AbstractMapGenerator):
    """
    Like JumpingMap, but ensures a path (cost==1) exists from start to target.

    kwargs:
      - p: float in [0,1] (required)
      - max_tries: int (optional, default 200)
    """

    @classmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: Coordinate,
        target: Coordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> np.ndarray:
        cls._validate_dims(n, m)
        cls._validate_Coordinate(n, m, start, "start")
        cls._validate_Coordinate(n, m, target, "target")

        p = float(kwargs.get("p", 0.4))
        cls._validate_p(p)

        max_tries = int(kwargs.get("max_tries", 200))
        if max_tries <= 0:
            raise ValueError("max_tries must be > 0.")

        for _ in range(max_tries):
            grid = JumpingMap.generate(n, m, start, target, rng, p=p)
            if cls._has_path_4neigh(grid, start, target):
                return grid

        # Fallback: carve a guaranteed path
        grid = JumpingMap.generate(n, m, start, target, rng, p=p)
        cls._carve_manhattan_path(grid, start, target)
        return grid


class UniformMap(AbstractMapGenerator):
    """
    Uniform random costs in [min_val, max_val], with min_val >= 1.

    kwargs:
      - min_val: float (required, >= 1)
      - max_val: float (required, >= min_val)
    """

    @classmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: Coordinate,
        target: Coordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> np.ndarray:
        cls._validate_dims(n, m)
        cls._validate_Coordinate(n, m, start, "start")
        cls._validate_Coordinate(n, m, target, "target")

        min_val = float(kwargs.get("min_val", 1))
        max_val = float(kwargs.get("min_val", 20))

        if min_val < 1.0:
            raise ValueError("min_val must be >= 1.0")
        if max_val < min_val:
            raise ValueError("max_val must be >= min_val")

        grid = np.empty((n, m), dtype=float)
        for i in range(n):
            for j in range(m):
                grid[i, j] = cls._uniform(rng, min_val, max_val)
        return grid


class ExponentialMap(AbstractMapGenerator):
    """
    Exponential random costs: 1 + Exp(scale), guaranteeing >= 1.

    kwargs:
      - scale: float (optional, default 1.0, must be > 0)
    """

    @classmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: Coordinate,
        target: Coordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> np.ndarray:
        cls._validate_dims(n, m)
        cls._validate_Coordinate(n, m, start, "start")
        cls._validate_Coordinate(n, m, target, "target")

        scale = float(kwargs.get("scale", 1.0))
        if scale <= 0:
            raise ValueError("scale must be > 0")

        grid = np.empty((n, m), dtype=float)
        for i in range(n):
            for j in range(m):
                grid[i, j] = 1.0 + cls._exponential(rng, scale=scale)
        return grid


class PerlinMap(AbstractMapGenerator):
    """
    Perlin noise based map generator.

    kwargs:
      - abruptness: float (optional, default 0.5, must be >= 0)
      - seed: int (optional)
    """

    @classmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: Coordinate,
        target: Coordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> np.ndarray:
        cls._validate_dims(n, m)
        cls._validate_Coordinate(n, m, start, "start")
        cls._validate_Coordinate(n, m, target, "target")

        abruptness = float(kwargs.get("abruptness", 0.5))
        if abruptness < 0:
            raise ValueError("abruptness must be >= 0")

        highest = float(kwargs.get("highest", n*m))
        if highest <= 1.0:
            raise ValueError("highest must be > 1.0")

        grid = perlin_generator(n, m, abruptness=abruptness, rng=rng)
        # Shift to ensure all costs >= 1.0
        min_cost = np.min(grid)
        if min_cost < 1.0:
            grid += (1.0 - min_cost)

        # Scale to ensure max cost == highest
        max_cost = np.max(grid)
        scale = highest / max_cost
        grid *= scale

        return grid


# ---------------- Factory / registry ----------------

class MapFactory:
    """
    Factory to create maps by name.

    Example:
        grid = MapFactory.generate("column", n, m, start, target, rng, p=0.2)
    """

    _REGISTRY: Dict[str, Type[AbstractMapGenerator]] = {
        "empty": EmptyMap,
        "bimodel": BimodelMap,
        "jumping": JumpingMap,
        "column": ColumnMap,
        "uniform": UniformMap,
        "exponential": ExponentialMap,
        "perlin": PerlinMap,
        # optional aliases
        "exp": ExponentialMap,
        "uni": UniformMap,
        "random": UniformMap,
    }

    @classmethod
    def generate(
        cls,
        name: str,
        n: int,
        m: int,
        start: Coordinate,
        target: Coordinate,
        rng: RandomGenerator,
        integer: bool = False,
        **kwargs: Any,
    ) -> np.ndarray:
        key = name.strip().lower()
        if key not in cls._REGISTRY:
            available = ", ".join(sorted(cls._REGISTRY.keys()))
            raise ValueError(f"Unknown map generator '{name}'. Available: {available}")

        gen_cls = cls._REGISTRY[key]
        map = gen_cls.generate(n, m, start, target, rng, **kwargs)

        if integer:
            map = np.round(map).astype(int)

        return map



    @classmethod
    def available_generation_methods(cls) -> List[str]:
        """Returns a sorted list of available map generation method names."""
        l = list(cls._REGISTRY.keys())
        # Remove aliases (those that map to the same class as another key)
        unique_classes = set()
        unique_keys = []
        for key in l:
            gen_cls = cls._REGISTRY[key]
            if gen_cls not in unique_classes:
                unique_classes.add(gen_cls)
                unique_keys.append(key)
        return sorted(unique_keys)
