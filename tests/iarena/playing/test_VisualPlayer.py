"""Tests for the generic visual-interactive player."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import pytest

from iarena.interfacing.IGameRules import IGameRules
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPosition import IPosition
from iarena.interfacing.ScoreBoard import ScoreBoard
from iarena.playing.VisualPlayer import VisualPlayer


@dataclass(frozen=True, slots=True)
class DummyMovement(IMovement):
    """Minimal movement used by visual-player tests."""

    value: str


class DummyPosition(IPosition):
    """Minimal position used by visual-player tests."""

    def next_player(self) -> int:
        """Return next player index.

        Args:
            None.

        Returns:
            Always ``0``.
        """
        return 0


class DummyRules(IGameRules):
    """Simple one-player rules for visual-player tests."""

    def __init__(self, movements: list[DummyMovement]) -> None:
        """Initialize deterministic rule set.

        Args:
            movements: Legal movements yielded for any position.

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
        """Return initial position.

        Args:
            None.

        Returns:
            Dummy position.
        """
        return DummyPosition()

    def next_position(self, movement: IMovement, position: IPosition) -> IPosition:
        """Return unchanged position.

        Args:
            movement: Unused movement.
            position: Current position.

        Returns:
            Same position.
        """
        del movement
        return position

    def possible_movements(self, position: IPosition) -> Iterator[IMovement]:
        """Yield legal movements.

        Args:
            position: Current position.

        Returns:
            Iterator with configured movements.
        """
        del position
        yield from self._movements

    def finished(self, position: IPosition) -> bool:
        """Return finished state.

        Args:
            position: Current position.

        Returns:
            Always ``False``.
        """
        del position
        return False

    def score(self, position: IPosition) -> ScoreBoard:
        """Return zero score board.

        Args:
            position: Current position.

        Returns:
            Scoreboard with one score.
        """
        del position
        board = ScoreBoard(1)
        board.define_score(0, 0.0)
        return board


class _FakeContainer:
    """Small container test double that simulates buttons."""

    def __init__(self, clicked_key: str | None = None) -> None:
        """Initialize fake button behavior.

        Args:
            clicked_key: Button key to return as clicked.

        Returns:
            None.
        """
        self._clicked_key = clicked_key
        self.labels: list[str] = []

    def button(self, label: str, key: str) -> bool:
        """Return whether this button should be treated as clicked.

        Args:
            label: Button label.
            key: Button key.

        Returns:
            ``True`` only for the configured clicked key.
        """
        self.labels.append(label)
        return key == self._clicked_key


def test_visual_player_selects_clicked_movement() -> None:
    """Visual player should return the movement mapped to clicked button.

    Args:
        None.

    Returns:
        None.
    """
    movements = [DummyMovement("left"), DummyMovement("right")]
    rules = DummyRules(movements=movements)
    player = VisualPlayer()
    player.starting_game(rules, player_index=0)
    container = _FakeContainer(clicked_key="test.move.1")

    selected = player.play_from_ui(
        rules.first_position(),
        ui_context={
            "container": container,
            "possible_movements": tuple(movements),
            "key_prefix": "test",
        },
    )

    assert selected == DummyMovement("right")
    assert container.labels == ["1. DummyMovement(value='left')", "2. DummyMovement(value='right')"]


def test_visual_player_requires_starting_game_and_valid_context() -> None:
    """Visual player should validate startup state and UI context.

    Args:
        None.

    Returns:
        None.
    """
    rules = DummyRules(movements=[DummyMovement("up")])
    position = rules.first_position()
    player = VisualPlayer()

    with pytest.raises(RuntimeError):
        player.play_from_ui(position, ui_context={"container": _FakeContainer()})

    player.starting_game(rules, player_index=0)
    with pytest.raises(ValueError):
        player.play_from_ui(position, ui_context=None)


def test_visual_player_requires_a_clicked_button_and_legal_movements() -> None:
    """Visual player should report missing click and empty movement lists.

    Args:
        None.

    Returns:
        None.
    """
    rules = DummyRules(movements=[DummyMovement("up")])
    player = VisualPlayer()
    player.starting_game(rules, player_index=0)
    position = rules.first_position()

    with pytest.raises(RuntimeError):
        player.play_from_ui(position, ui_context={"container": _FakeContainer(clicked_key=None)})

    empty_rules = DummyRules(movements=[])
    player.starting_game(empty_rules, player_index=0)
    with pytest.raises(RuntimeError):
        player.play_from_ui(empty_rules.first_position(), ui_context={"container": _FakeContainer(clicked_key=None)})
