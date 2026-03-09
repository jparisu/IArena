"""Defines a generic terminal human player implementation placeholder."""

from __future__ import annotations

from typing import TYPE_CHECKING

from iarena.playing.HumanPlayer import HumanPlayer

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules
    from iarena.playing.PlayerIndex import PlayerIndex


class PolyvalentTerminalPlayer(HumanPlayer):
    """Generic terminal human player driven by indexed movement selection for any game.

    Purpose:
        Provides the `PolyvalentTerminalPlayer` type within the IArena architecture.
    How it works:
        Encapsulates behavior through its public API and type contracts defined in this class body.
    Used for:
        Building game, mapping, utility, or protocol components that can be composed by other modules.
    Public Attributes:
        None declared at class level in this base definition.
    """

    def __init__(self, name: str | None = None) -> None:
        """Initialize the player with an optional name.

        Args:
            name (str | None): Optional name for the player. If None, a default name is assigned.

        Returns:
            None.
        """
        super().__init__(name=name)

    def name(self) -> str:
        """Return a stable identifier for this terminal player type.

        What it does:
            Exposes the recognizable name required by the player protocol.
        How it works:
            Placeholder method for subclasses or future concrete implementation.
        Args:
            None.
        Returns:
            str: Canonical terminal-player identifier.
        """
        return "polyvalent-terminal"

    def play(self, pos: Position) -> Movement:
        """Choose and return the next movement for the given position.

        What it does:
            Defines the player decision operation for terminal-driven interaction.
        How it works:
            Placeholder method to be implemented with input capture logic.
        Args:
            pos (Position): Current game position where this player must act.
        Returns:
            Movement: Movement selected by the terminal interaction strategy.
        """
        possible_movements = list(pos.get_rules().possible_movements(pos))
        if not possible_movements:
            raise ValueError("No legal movements available for PolyvalentTerminalPlayer.")

        render = getattr(self, "render", None)
        output_fnc = getattr(render, "output_fnc", print)
        input_fnc = getattr(render, "input_fnc", input)
        if not callable(output_fnc) or not callable(input_fnc):
            raise TypeError("`render` must expose callable `output_fnc` and `input_fnc` attributes.")

        output_fnc("Select one movement by index:")
        for movement_index, movement in enumerate(possible_movements):
            output_fnc(f"{movement_index}: {movement}")

        while True:
            raw_index = input_fnc("Index: ").strip()
            try:
                selected_index = int(raw_index)
            except ValueError:
                output_fnc("Invalid index. Please enter an integer value.")
                continue

            if 0 <= selected_index < len(possible_movements):
                return possible_movements[selected_index]
            output_fnc("Selected movement index is out of bounds.")

    def starting_game(self, rules: Rules, player_index: PlayerIndex) -> None:
        """Initialize runtime state before the first turn of a game.

        What it does:
            Defines the setup operation invoked at game start.
        How it works:
            Placeholder method for wiring rules, index, and rendering context.
        Args:
            rules (Rules): Rules object that governs the upcoming game.
            player_index (PlayerIndex): Index assigned to this player.
        Returns:
            None: This hook performs setup side effects only.
        """
        self._rules = rules
        self._player_index = player_index
