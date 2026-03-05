"""Tests for GoldMine Streamlit-playable player."""

from __future__ import annotations

import pytest

from iarena.gaming.GoldMine.GoldMineGameRules import GoldMineGameRules
from iarena.gaming.GoldMine.GoldMineMovement import GoldMineMovement
from iarena.gaming.GoldMine.GoldMinePlayablePlayer import GoldMinePlayablePlayer
from iarena.utilizing.square_map.SquareMap import Coordinate, Direction, SquareMap


class _FakeButtonContainer:
    """Small button-capable container used inside column layouts."""

    def __init__(self, selected_key: str | None) -> None:
        """Initialize button behavior for one nested container.

        Args:
            selected_key: Key that should be treated as clicked.

        Returns:
            None.
        """
        self._selected_key = selected_key
        self.messages: list[str] = []

    def button(self, label: str, key: str, disabled: bool = False) -> bool:
        """Return whether the configured key is clicked.

        Args:
            label: Button label.
            key: Button key.
            disabled: Whether button is disabled.

        Returns:
            ``True`` only for the configured key.
        """
        del label
        return (not disabled) and key == self._selected_key

    def write(self, value: object) -> None:
        """Store text writes for inspection.

        Args:
            value: Rendered value.

        Returns:
            None.
        """
        self.messages.append(str(value))


class _FakeContainer(_FakeButtonContainer):
    """Small container that provides streamlit-like column layout."""

    def __init__(self, selected_key: str | None = None) -> None:
        """Initialize container with optional clicked key.

        Args:
            selected_key: Key that should be treated as clicked.

        Returns:
            None.
        """
        super().__init__(selected_key=selected_key)

    def columns(self, n_columns: int) -> tuple[_FakeButtonContainer, ...]:
        """Return nested fake containers for a row layout.

        Args:
            n_columns: Number of requested columns.

        Returns:
            Tuple of fake button containers.
        """
        return tuple(_FakeButtonContainer(selected_key=self._selected_key) for _ in range(n_columns))


def _build_rules() -> GoldMineGameRules:
    """Build deterministic rules for playable-player tests.

    Args:
        None.

    Returns:
        Configured GoldMine rules.
    """
    return GoldMineGameRules(
        cost_map=SquareMap([[1.0, 2.0], [3.0, 4.0]]),
        target=Coordinate(1, 1),
        start=Coordinate(0, 0),
    )


def test_playable_player_rejects_non_ui_play_entrypoint() -> None:
    """Playable player should require the UI-specific method.

    Args:
        None.

    Returns:
        None.
    """
    player = GoldMinePlayablePlayer()

    with pytest.raises(RuntimeError):
        player.play(_build_rules().first_position())


def test_playable_player_returns_ui_selected_movement() -> None:
    """Playable player should return movement selected in UI controls.

    Args:
        None.

    Returns:
        None.
    """
    rules = _build_rules()
    player = GoldMinePlayablePlayer()
    position = rules.first_position()

    movement = player.play_from_ui(
        position,
        ui_context={"container": _FakeContainer(selected_key="goldmine.Right")},
    )

    assert movement == GoldMineMovement(Direction.Right)


def test_playable_player_validates_context_and_position_types() -> None:
    """Playable player should validate provided position and UI context.

    Args:
        None.

    Returns:
        None.
    """
    player = GoldMinePlayablePlayer()
    position = _build_rules().first_position()

    with pytest.raises(TypeError):
        player.play_from_ui(object(), ui_context={"container": _FakeContainer()})
    with pytest.raises(ValueError):
        player.play_from_ui(position, ui_context=None)
