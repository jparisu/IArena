"""Tests for the terminal-interactive generic player."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import pytest

from iarena.interfacing.IGameRules import IGameRules
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPosition import IPosition
from iarena.interfacing.ScoreBoard import ScoreBoard
from iarena.playing.TerminalPlayer import TerminalPlayer


@dataclass(frozen=True, slots=True)
class DummyMovement(IMovement):
    """Minimal movement for terminal-player tests."""

    value: str


class DummyPosition(IPosition):
    """Minimal position for terminal-player tests."""

    def next_player(self) -> int:
        """Return the next player index.

        Args:
            None.

        Returns:
            Always ``0``.
        """
        return 0


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


def test_terminal_player_selects_user_movement() -> None:
    """Terminal player should return the movement selected by the user.

    Args:
        None.

    Returns:
        None.
    """
    inputs = iter(["2"])
    outputs: list[str] = []
    rules = DummyRules([DummyMovement("left"), DummyMovement("right")])
    player = TerminalPlayer(
        input_function=lambda _: next(inputs),
        output_function=outputs.append,
    )
    player.starting_game(rules, player_index=0)

    selected = player.play(rules.first_position())

    assert selected == DummyMovement("right")
    assert outputs[0] == "Possible movements:"


def test_terminal_player_reprompts_after_invalid_input() -> None:
    """Invalid terminal inputs should trigger a re-prompt.

    Args:
        None.

    Returns:
        None.
    """
    inputs = iter(["abc", "7", "1"])
    outputs: list[str] = []
    rules = DummyRules([DummyMovement("up"), DummyMovement("down")])
    player = TerminalPlayer(
        input_function=lambda _: next(inputs),
        output_function=outputs.append,
    )
    player.starting_game(rules, player_index=0)

    selected = player.play_from_terminal(rules.first_position())

    assert selected == DummyMovement("up")
    assert any("Invalid movement." in line for line in outputs)


def test_terminal_player_requires_starting_game_before_prompt() -> None:
    """Calling terminal play before starting_game should raise.

    Args:
        None.

    Returns:
        None.
    """
    player = TerminalPlayer(input_function=lambda _: "1", output_function=lambda _: None)

    with pytest.raises(RuntimeError):
        player.play_from_terminal(DummyPosition())


def test_terminal_player_raises_when_no_legal_movements() -> None:
    """No legal movements should raise a runtime error.

    Args:
        None.

    Returns:
        None.
    """
    rules = DummyRules([])
    player = TerminalPlayer(input_function=lambda _: "1", output_function=lambda _: None)
    player.starting_game(rules, player_index=0)

    with pytest.raises(RuntimeError):
        player.play(rules.first_position())
