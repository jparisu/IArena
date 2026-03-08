from __future__ import annotations

import pytest

from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


def test_init_sets_reproducible_seed_state() -> None:
    first = RandomGenerator(123)
    second = RandomGenerator(123)

    assert first.rand() == second.rand()


def test_rand_returns_value_in_unit_interval() -> None:
    rng = RandomGenerator(7)
    value = rng.rand()

    assert 0.0 <= value < 1.0


def test_random_is_alias_of_rand() -> None:
    with_rand = RandomGenerator(101)
    with_random = RandomGenerator(101)

    assert with_rand.rand() == with_random.random()


def test_choice_returns_element_from_sequence() -> None:
    rng = RandomGenerator(99)
    seq = ["a", "b", "c"]

    assert rng.choice(seq) in seq


def test_choice_raises_for_empty_sequence() -> None:
    rng = RandomGenerator(99)

    with pytest.raises(ValueError, match="Sequence is empty"):
        rng.choice([])


def test_set_seed_changes_sequence() -> None:
    rng = RandomGenerator(10)
    original = rng.rand()

    rng.set_seed(20)

    assert rng.rand() != original


def test_set_seed_with_consistent_true_updates_reset_target() -> None:
    rng = RandomGenerator(5)
    _ = rng.rand()

    rng.set_seed(42, consistent=True)
    first_after_set = rng.rand()
    rng.reset_seed()

    assert rng.rand() == first_after_set


def test_reset_seed_restores_initial_seed_by_default() -> None:
    rng = RandomGenerator(3)
    first_value = rng.rand()
    _ = rng.rand()

    rng.reset_seed()

    assert rng.rand() == first_value


def test_shuffle_mutates_sequence_in_place_deterministically_for_seed() -> None:
    values_a = [1, 2, 3, 4, 5]
    values_b = [1, 2, 3, 4, 5]

    RandomGenerator(11).shuffle(values_a)
    RandomGenerator(11).shuffle(values_b)

    assert values_a == values_b
    assert sorted(values_a) == [1, 2, 3, 4, 5]


def test_randint_returns_value_in_half_open_interval() -> None:
    rng = RandomGenerator(8)

    value = rng.randint(5, 2)

    assert 2 <= value < 5


def test_randint_raises_when_high_is_not_greater_than_low() -> None:
    rng = RandomGenerator(8)

    with pytest.raises(ValueError, match="high"):
        rng.randint(3, 3)
