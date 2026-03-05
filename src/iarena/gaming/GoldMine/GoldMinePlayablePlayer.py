"""Streamlit-playable player for the GoldMine game."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from iarena.gaming.GoldMine.GoldMine import GoldMineDirection
from iarena.gaming.GoldMine.GoldMineMovement import GoldMineMovement
from iarena.gaming.GoldMine.GoldMinePosition import GoldMinePosition
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPlayer import IPlayer
from iarena.interfacing.IPosition import IPosition


class GoldMinePlayablePlayer(IPlayer):
    """Human-controlled GoldMine player that reads movement from Streamlit UI."""

    def play(self, position: IPosition) -> IMovement:
        """Reject autonomous execution for this playable-only player.

        Args:
            position: Current position.

        Returns:
            Never returns.
        """
        del position
        raise RuntimeError("GoldMinePlayablePlayer requires play_from_ui()")

    def play_from_ui(self, position: IPosition, ui_context: Any | None = None) -> IMovement:
        """Choose one movement from directional UI controls.

        Args:
            position: Current GoldMine position.
            ui_context: UI context mapping that must provide ``container``.

        Returns:
            Movement selected by the user in Streamlit widgets.
        """
        if not isinstance(position, GoldMinePosition):
            raise TypeError(f"position must be GoldMinePosition, got {type(position).__name__}")
        if not isinstance(ui_context, Mapping) or "container" not in ui_context:
            raise ValueError("ui_context must be a mapping containing 'container'")

        container = ui_context["container"]
        key_prefix = str(ui_context.get("key_prefix", "goldmine"))
        available_cost_by_direction = {
            direction: cost for direction, cost in position.directions_with_cost()
        }
        if not available_cost_by_direction:
            raise RuntimeError("no legal movement available for GoldMinePlayablePlayer")

        top_row = container.columns(3)
        middle_row = container.columns(3)
        bottom_row = container.columns(3)

        selected_direction: GoldMineDirection | None = None

        def _direction_button(target_container: Any, direction: GoldMineDirection) -> None:
            """Render one directional button and capture click state.

            Args:
                target_container: Container where button is rendered.
                direction: Cardinal direction represented by the button.

            Returns:
                None.
            """
            nonlocal selected_direction
            movement_cost = available_cost_by_direction.get(direction)
            disabled = movement_cost is None
            label = (
                f"{direction.name} ({movement_cost:.2f})"
                if movement_cost is not None
                else f"{direction.name} (N/A)"
            )
            if target_container.button(
                label,
                key=f"{key_prefix}.{direction.name}",
                disabled=disabled,
            ):
                selected_direction = direction

        _direction_button(top_row[1], GoldMineDirection.Up)
        _direction_button(middle_row[0], GoldMineDirection.Left)
        middle_row[1].write("Current")
        _direction_button(middle_row[2], GoldMineDirection.Right)
        _direction_button(bottom_row[1], GoldMineDirection.Down)

        if selected_direction is None:
            raise RuntimeError("movement not selected yet")
        return GoldMineMovement(direction=selected_direction)
