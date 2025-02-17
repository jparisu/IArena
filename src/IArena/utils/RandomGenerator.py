import random

class RandomGenerator:
    def __init__(self, seed):
        self.initial_seed = seed
        self.seed = seed
        self.rng = random.Random(seed)

    def rand(self):
        return self.rng.random()

    def randint(self, a, b):
        return self.rng.randint(a, b)

    def choice(self, seq):
        return self.rng.choice(seq)

    def set_seed(self, seed):
        self.initial_seed = seed
        self.reset_seed()

    def reset_seed(self):
        self.set_seed(self.initial_seed)
