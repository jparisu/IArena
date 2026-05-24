"""Declares a no-op view used when rendering and input capture are unnecessary."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules
    from iarena.visualizing.Canvas import Canvas

from iarena.visualizing.View import View


class EmptyView(View):
    """No-op view used when rendering and input capture are unnecessary.

    Purpose:
        Provides the `EmptyView` type within the IArena architecture.
    How it works:
        Represents a visualization endpoint that intentionally performs no frontend interaction.
    Used for:
        Running non-interactive matches, testing flows, or batch evaluations without UI output.
    Public Attributes:
        Inherits shared view attributes from `View`.
    """

    def render_info(self, rules: Rules, canvas: Canvas) -> None:
        """Render no-op information for non-visual games.

        Args:
            rules: Rules instance that defines the game mechanics being played.
            canvas: Target canvas abstraction associated with the rendering pipeline.

        Returns:
            None.

        """
        _ = rules
        _ = canvas

    def render_state(self, pos: Position, canvas: Canvas) -> None:
        """Render no-op state for non-visual games.

        Args:
            pos: Current game position that would be shown in an interactive frontend.
            canvas: Target canvas abstraction associated with the rendering pipeline.

        Returns:
            None.

        """
        _ = pos
        _ = canvas

    def capture_input(self, *args: Any) -> Movement:
        """Capture no-op input for non-interactive games.

        Args:
            *args: Optional frontend-specific context values.

        Returns:
            Movement produced by the input system.

        Raises:
            RuntimeError: Always, because `EmptyView` intentionally does not support user interaction.
        """
        _ = args
        raise RuntimeError("EmptyView does not support input capture.")
