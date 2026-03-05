"""Tests for the generic random player."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import pytest

from iarena.interfacing.IGameRules import IGameRules
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPosition import IPosition
from iarena.interfacing.ScoreBoard import ScoreBoard
from iarena.playing.RandomPlayer import RandomPlayer
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


@dataclass(frozen=True, slots=True)
class DummyMovement(IMovement):
    """Minimal movement for generic-player tests."""

    value: str


class DummyPosition(IPosition):
    """Minimal position for generic-player tests."""

    def __init__(self, player: int = 0) -> None:
        """Initialize position with a fixed next player index.

        Args:
            player: Index to return from :meth:`next_player`.

        Returns:
            None.
        """
        self._player = player

    def next_player(self) -> int:
        """Return the next player index.

        Args:
            None.

        Returns:
            Player index.
        """
        return self._player


class DummyRules(IGameRules):
    """Simple rules exposing a predefined list of legal movements."""

    def __init__(self, movements: list[DummyMovement]) -> None:
        """Initialize rules with a fixed movement list.

        Args:
            movements: Legal movements returned by :meth:`possible_movements`.

        Returns:
            None.
        """
        self._movements = movements

    def n_players(self) -> int:
        """Return number of players.

        Args:
            None.

        Returns:
            Always ``1``.
        """
        return 1

    def first_position(self) -> IPosition:
        """Return an initial position.

        Args:
            None.

        Returns:
            Initial position object.
        """
        return DummyPosition()

    def next_position(self, movement: IMovement, position: IPosition) -> IPosition:
        """Return unchanged position.

        Args:
            movement: Unused movement.
            position: Current position.

        Returns:
            Same position object.
        """
        del movement
        return position

    def possible_movements(self, position: IPosition) -> Iterator[IMovement]:
        """Yield legal movements for a position.

        Args:
            position: Current position.

        Returns:
            Iterator over configured movements.
        """
        del position
        yield from self._movements

    def finished(self, position: IPosition) -> bool:
        """Return whether game is finished.

        Args:
            position: Current position.

        Returns:
            Always ``False``.
        """
        del position
        return False

    def score(self, position: IPosition) -> ScoreBoard:
        """Return a zero scoreboard.

        Args:
            position: Current position.

        Returns:
            Scoreboard for one player.
        """
        del position
        return ScoreBoard(1)


def test_random_player_uses_seed_deterministically() -> None:
    """Players with same seed should pick the same movement.

    Args:
        None.

    Returns:
        None.
    """
    movements = [DummyMovement("a"), DummyMovement("b"), DummyMovement("c")]
    rules = DummyRules(movements)
    position = rules.first_position()

    first = RandomPlayer(seed=9)
    second = RandomPlayer(seed=9)
    first.starting_game(rules, player_index=0)
    second.starting_game(rules, player_index=0)

    assert first.play(position) == second.play(position)


def test_random_player_uses_provided_generator() -> None:
    """Provided generator should drive movement selection.

    Args:
        None.

    Returns:
        None.
    """
    movements = [DummyMovement("a"), DummyMovement("b"), DummyMovement("c")]
    rules = DummyRules(movements)
    position = rules.first_position()

    generator = RandomGenerator(seed=13)
    expected = RandomGenerator(seed=13).choice(movements)
    player = RandomPlayer(random_generator=generator)
    player.starting_game(rules, player_index=0)

    assert player.play(position) == expected


def test_random_player_without_seed_still_selects_legal_movement() -> None:
    """No-seed construction should still choose one legal movement.

    Args:
        None.

    Returns:
        None.
    """
    movements = [DummyMovement("left"), DummyMovement("right")]
    rules = DummyRules(movements)
    player = RandomPlayer()
    player.starting_game(rules, player_index=0)

    selected = player.play(rules.first_position())

    assert selected in movements


def test_random_player_rejects_generator_and_seed_combination() -> None:
    """Passing generator and seed at once should raise.

    Args:
        None.

    Returns:
        None.
    """
    with pytest.raises(ValueError):
        RandomPlayer(random_generator=RandomGenerator(seed=1), seed=5)


def test_random_player_requires_starting_game_before_play() -> None:
    """Calling play before starting_game should raise.

    Args:
        None.

    Returns:
        None.
    """
    player = RandomPlayer(seed=1)

    with pytest.raises(RuntimeError):
        player.play(DummyPosition())


def test_random_player_raises_when_no_legal_movements() -> None:
    """Empty legal-movement list should raise.

    Args:
        None.

    Returns:
        None.
    """
    rules = DummyRules([])
    player = RandomPlayer(seed=1)
    player.starting_game(rules, player_index=0)

    with pytest.raises(RuntimeError):
        player.play(rules.first_position())
