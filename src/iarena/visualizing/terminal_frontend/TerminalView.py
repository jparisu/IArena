"""Declares the abstract terminal frontend contract for game-specific terminal views."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules
    from iarena.visualizing.Canvas import Canvas

from iarena.visualizing.View import View


class TerminalView(View, ABC):
    """Abstract terminal frontend contract for game-specific terminal views.

    Purpose:
        Provides the `TerminalView` type within the IArena architecture.
    How it works:
        Standardizes terminal-oriented rendering and input behavior for concrete game frontends.
    Used for:
        Implementing command-line game interfaces with text-based state and movement interaction.
    Public Attributes:
        input_fnc: Input callable used to collect user text in terminal executions.
        output_fnc: Output callable used to display formatted text in terminal executions.
    """

    input_fnc: Any = input
    output_fnc: Any = print

    def render_info(self, rules: Rules, canvas: Canvas) -> None:
        """Render terminal info layer using default terminal frontend behavior.

        Args:
            rules: Rules instance that defines the game mechanics for the current match.
            canvas: Target canvas abstraction linked to this terminal rendering pass.

        Returns:
            None.

        """
        _ = canvas
        self._emit_text(self.get_str_info(rules))

    def render_state(self, pos: Position, canvas: Canvas) -> None:
        """Render terminal state layer using default terminal frontend behavior.

        Args:
            pos: Current game position that should be represented in terminal output.
            canvas: Target canvas abstraction linked to this terminal rendering pass.

        Returns:
            None.

        """
        _ = canvas

        section_line = "=" * 72
        self._emit_text("\n")
        self._emit_text(section_line)
        self._emit_text(self.get_str_state(pos))
        self._emit_text(section_line)
        self._emit_text("\n")


    def _emit_text(self, text: str) -> None:
        """Send one formatted text block to the configured output callable.

        Args:
            text: String payload to forward to the terminal output function.

        Returns:
            None.
        """
        self.output_fnc(text)

    @abstractmethod
    def get_str_info(self, rules: Rules) -> str:
        """Return the formatted info text representation for terminal output.

        Args:
            rules: Rules instance used to extract user-facing game information.

        Returns:
            Formatted text block describing game information for terminal display.

        Raises:
            NotImplementedError: Always, subclasses must implement this method.
        """
        raise NotImplementedError

    @abstractmethod
    def get_str_state(self, position: Position) -> str:
        """Return the formatted state text representation for terminal output.

        Args:
            position: Current game position to transform into terminal-friendly text.

        Returns:
            Formatted text block describing the current game state.

        Raises:
            NotImplementedError: Always, subclasses must implement this method.
        """
        raise NotImplementedError

    @abstractmethod
    def capture_input(self, input: str) -> Movement:
        """Convert a terminal input string into a movement.

        Args:
            input: Raw terminal text entered by the user.

        Returns:
            Movement parsed from the provided terminal input text.

        Raises:
            NotImplementedError: Always, subclasses must implement this method.
        """
        raise NotImplementedError
