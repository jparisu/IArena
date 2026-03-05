"""Generic Streamlit-interactive player implementation for IArena games."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from iarena.interfacing.IGameRules import IGameRules
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPlayer import IPlayer, PlayerIndex
from iarena.interfacing.IPosition import IPosition


class VisualPlayer(IPlayer):
    """Human-controlled player that selects movements via visual buttons."""

    def __init__(self, name: str | None = None) -> None:
        """Initialize a visual player.

        Args:
            name: Optional display name.

        Returns:
            None.
        """
        super().__init__(name=name)
        self._rules: IGameRules | None = None

    def starting_game(self, rules: IGameRules, player_index: PlayerIndex) -> None:
        """Store game rules before interactive movement requests.

        Args:
            rules: Rules object used by the game.
            player_index: Index assigned to this player.

        Returns:
            None.
        """
        del player_index
        self._rules = rules

    def play(self, position: IPosition) -> IMovement:
        """Reject autonomous ``play`` usage for visual-only interaction.

        Args:
            position: Current game position.

        Returns:
            Never returns.
        """
        del position
        raise RuntimeError("VisualPlayer requires play_from_ui()")

    def play_from_ui(self, position: IPosition, ui_context: Any | None = None) -> IMovement:
        """Render one button per legal movement and return clicked option.

        Args:
            position: Current game position.
            ui_context: Mapping that must contain ``container`` and may include
                ``possible_movements`` and ``key_prefix``.

        Returns:
            Selected movement.
        """
        if self._rules is None:
            raise RuntimeError("VisualPlayer requires starting_game() before play_from_ui()")
        if not isinstance(ui_context, Mapping) or "container" not in ui_context:
            raise ValueError("ui_context must be a mapping containing 'container'")

        container = ui_context["container"]
        possible_raw = ui_context.get("possible_movements")
        if possible_raw is None:
            movements = tuple(self._rules.possible_movements(position))
        else:
            movements = tuple(movement for movement in possible_raw if isinstance(movement, IMovement))
        if not movements:
            raise RuntimeError("no legal movement available for VisualPlayer")

        key_prefix = str(ui_context.get("key_prefix", "visual-player"))
        for index, movement in enumerate(movements):
            label = str(movement)
            button_label = f"{index + 1}. {label}"
            button_key = f"{key_prefix}.move.{index}"
            if container.button(button_label, key=button_key):
                return movement

        raise RuntimeError("movement not selected yet")
