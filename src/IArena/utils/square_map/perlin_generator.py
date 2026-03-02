from noise import pnoise2
import random
import math
import numpy as np

from IArena.utils.RandomGenerator import RandomGenerator

def perlin_value_generator(
        i: int,
        j: int,
        base: int,
        scale: int,
        persistence: float = 0.5,
        octaves: int = 2,
        lacunarity: float = 2.0
    ) -> int:
    """
    Generates a random value for a cell of a terrain using Perlin noise

    :param i: row of the cell
    :param j: column of the cell
    :param base: base value of the cell
    :param persistence: level of persistence of the terrain (0 = smooth, 1 = abrupt)
    :param scale: index of change of the terrain (0 = smooth, 1 = abrupt)
    :param octave: number of octaves of the noise
    :param lacunarity: lacunarity of the noise
    """

    return pnoise2(
        (base + i) / scale,
        (base + j) / scale,
        persistence=persistence,
        octaves=octaves,
        lacunarity=lacunarity)


def perlin_generator(
        n: int,
        m: int,
        abruptness: float = 0.5,
        rng: RandomGenerator = None
) -> np.matrix:
    """
    TODO
    """
    abruptness *= 25
    abruptness = max(0.0001, abruptness)

    if rng is None:
        rng = RandomGenerator()
    base = rng.randint(0, 100000)

    scale = math.sqrt(n * m) / abruptness

    map = np.zeros((n,m))
    for i in range(n):
        for j in range(m):
            map[i][j] = perlin_value_generator(
                i, j, base, scale)
    return map
