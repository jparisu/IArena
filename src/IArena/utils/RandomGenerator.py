import random

class RandomGenerator:
    def __init__(self, seed=0):
        if seed is None:
            seed = random.randint(0, 2**32 - 1)
        self.initial_seed = seed
        self.seed = seed
        self.rng = random.Random(seed)

    def rand(self):
        return self.rng.random()

    def random(self):
        return self.rand()

    def randint(self, a, b):
        return self.rng.randint(a, b)

    def choice(self, seq):
        return self.rng.choice(seq)

    def set_seed(self, seed, consistent=False):
        if consistent:
            self.seed = seed
        self.rng = random.Random(seed)

    def reset_seed(self):
        self.set_seed(self.initial_seed, consistent=False)

    def shuffle(self, x):
        self.rng.shuffle(x)

    def randint(self, high: int, low: int = 0) -> int:
        """
        WARNING: high is not choosable
        """
        return self.rng.randint(low, high-1)
