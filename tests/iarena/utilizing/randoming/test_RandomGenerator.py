"""Tests for the seedable random generator wrapper."""

from __future__ import annotations

import importlib

random_generator_module = importlib.import_module("iarena.utilizing.randoming.RandomGenerator")
RandomGenerator = random_generator_module.RandomGenerator


def test_init_with_none_seed_uses_random_module(monkeypatch) -> None:
    """`seed=None` should pick a generated integer seed."""
    monkeypatch.setattr(random_generator_module.random, "randint", lambda a, b: 12345)
    rng = RandomGenerator(seed=None)
    assert rng.initial_seed == 12345
    assert rng.seed == 12345


def test_rand_and_random_alias_share_same_stream() -> None:
    """`random()` is an alias to `rand()` and should be reproducible."""
    rng = RandomGenerator(seed=7)
    first = rng.rand()
    rng.reset_seed()
    assert rng.random() == first


def test_choice_and_shuffle_and_randint_bounds() -> None:
    """Collection helpers should behave deterministically with a fixed seed."""
    rng = RandomGenerator(seed=10)
    values = [1, 2, 3, 4]

    chosen = rng.choice(values)
    assert chosen in values

    to_shuffle = [1, 2, 3, 4, 5]
    rng.shuffle(to_shuffle)
    assert sorted(to_shuffle) == [1, 2, 3, 4, 5]

    samples = [rng.randint(high=8, low=3) for _ in range(25)]
    assert all(3 <= val < 8 for val in samples)


def test_set_seed_consistent_flag_and_reset_seed() -> None:
    """Seed management should update stream and optional tracked seed."""
    rng = RandomGenerator(seed=1)
    original_seed = rng.seed

    rng.set_seed(999, consistent=False)
    assert rng.seed == original_seed

    rng.set_seed(5, consistent=True)
    assert rng.seed == 5

    first_with_initial = RandomGenerator(seed=1).rand()
    rng.reset_seed()
    assert rng.rand() == first_with_initial
