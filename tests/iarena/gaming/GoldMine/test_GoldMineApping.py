"""Tests for GoldMine Streamlit page integration."""

from __future__ import annotations

from typing import Any

import pytest

from iarena.apping.AppingEngine import run_single_player_optimization_game
from iarena.apping.AppingModels import OptimizationViewState
from iarena.gaming.GoldMine.GoldMineApping import build_goldmine_streamlit_page
from iarena.gaming.GoldMine.GoldMineGameRules import GoldMineGameRules
from iarena.gaming.GoldMine.GoldMinePlayablePlayer import GoldMinePlayablePlayer
from iarena.gaming.GoldMine.GoldMinePlayer import GoldMinePlayer


class _FakeContainer:
    """Simple Streamlit-like container used by GoldMine page tests."""

    def __init__(self) -> None:
        """Initialize fake widget and output state.

        Args:
            None.

        Returns:
            None.
        """
        self.messages: list[str] = []
        self.code_values: list[str] = []
        self.select_values: dict[str, object] = {}

    def markdown(self, value: str) -> None:
        """Store markdown content.

        Args:
            value: Markdown value.

        Returns:
            None.
        """
        self.messages.append(value)

    def number_input(
        self,
        label: str,
        min_value: int,
        max_value: int,
        value: int,
        step: int,
    ) -> int:
        """Return configured value or default one.

        Args:
            label: Widget label.
            min_value: Minimum value.
            max_value: Maximum value.
            value: Default value.
            step: Step value.

        Returns:
            Chosen integer.
        """
        del min_value, max_value, step
        selected = self.select_values.get(label)
        if selected is None:
            return value
        return int(selected)

    def selectbox(self, label: str, options: tuple[Any, ...]) -> Any:
        """Return configured selection or first option.

        Args:
            label: Widget label.
            options: Candidate options.

        Returns:
            Selected option.
        """
        if label in self.select_values:
            return self.select_values[label]
        return options[0]

    def subheader(self, value: str) -> None:
        """Store subheader content.

        Args:
            value: Subheader value.

        Returns:
            None.
        """
        self.messages.append(value)

    def write(self, value: object) -> None:
        """Store generic text output.

        Args:
            value: Value to render.

        Returns:
            None.
        """
        self.messages.append(str(value))

    def code(self, value: str) -> None:
        """Store code block output.

        Args:
            value: Code text.

        Returns:
            None.
        """
        self.code_values.append(value)

    def expander(self, label: str, expanded: bool = False) -> _FakeContainer:
        """Return same fake container for collapsible sections.

        Args:
            label: Expander label.
            expanded: Initial expanded state.

        Returns:
            This same fake container.
        """
        del label, expanded
        return self


def test_build_goldmine_streamlit_page_configuration_and_rules() -> None:
    """GoldMine page should expose config UI and build valid game rules.

    Args:
        None.

    Returns:
        None.
    """
    page = build_goldmine_streamlit_page()
    container = _FakeContainer()
    container.select_values = {
        "Rows": 4,
        "Columns": 5,
        "Seed": 7,
        "Map generator": "uniform",
        "Hint mode": "compass",
    }

    config = page.render_configuration(container)
    rules = page.build_rules(config)
    player_factories = page.available_player_factories()

    assert page.key == "goldmine"
    assert isinstance(rules, GoldMineGameRules)
    assert isinstance(player_factories["Playable"](), GoldMinePlayablePlayer)
    assert rules.n_players() == 1
    assert rules.start_coordinate().x == 0
    assert rules.target_coordinate().x == 3
    assert rules.target_coordinate().y == 4


def test_goldmine_streamlit_page_renderers_use_view_state() -> None:
    """GoldMine page render callbacks should output state and secret map details.

    Args:
        None.

    Returns:
        None.
    """
    page = build_goldmine_streamlit_page()
    rules = page.build_rules({"rows": 3, "cols": 3, "seed": 0, "map_method": "uniform", "hint_mode": "compass"})
    replay = run_single_player_optimization_game(rules=rules, player=GoldMinePlayer(), turn_limit=40)
    frame = replay.frame_at(0)
    view_state = OptimizationViewState(
        replay=replay,
        frame_index=0,
        frame=frame,
        possible_movements=tuple(replay.rules.possible_movements(frame.position)),
    )
    container = _FakeContainer()

    page.render_position(container, view_state)
    assert any("Accumulated cost:" in value for value in container.messages)

    if page.render_secret_information is None:
        raise AssertionError("GoldMine page must define secret information renderer")
    page.render_secret_information(container, view_state)
    assert container.code_values


def test_goldmine_streamlit_page_renderers_validate_position_type() -> None:
    """GoldMine render callbacks should reject non-GoldMine position objects.

    Args:
        None.

    Returns:
        None.
    """
    page = build_goldmine_streamlit_page()
    rules = page.build_rules({"rows": 2, "cols": 2, "seed": 0, "map_method": "uniform", "hint_mode": "none"})
    replay = run_single_player_optimization_game(rules=rules, player=GoldMinePlayer(), turn_limit=20)
    frame = replay.frame_at(0)
    invalid_frame = type(frame)(
        turn_index=frame.turn_index,
        position=object(),
        score=frame.score,
        movement_to_next=frame.movement_to_next,
    )
    view_state = OptimizationViewState(
        replay=replay,
        frame_index=0,
        frame=invalid_frame,
        possible_movements=tuple(),
    )
    container = _FakeContainer()

    with pytest.raises(TypeError):
        page.render_position(container, view_state)

    if page.render_secret_information is None:
        raise AssertionError("GoldMine page must define secret information renderer")
    with pytest.raises(TypeError):
        page.render_secret_information(container, view_state)
