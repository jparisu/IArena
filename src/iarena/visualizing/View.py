"""Declares the abstract view contract for rendering game state and capturing input."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules
    from iarena.playing.Player import Player
    from iarena.visualizing.Canvas import Canvas


class View(ABC):
    """Abstract view responsible for rendering state and handling input.

    Purpose:
        Provides the `View` type within the IArena architecture.
    How it works:
        Defines a shared rendering/input abstraction for concrete frontends.
    Used for:
        Implementing terminal, streamlit, or other visualization frontends for games.
    Public Attributes:
        players: Ordered collection of players associated with the rendered match context.
    """

    players: list[Player]

    @abstractmethod
    def render_info(self, rules: Rules, canvas: Canvas) -> None:
        """Render static or contextual game information into a canvas.

        Args:
            rules: Rules instance that defines the game mechanics being visualized.
            canvas: Target canvas abstraction where information should be rendered.

        Returns:
            None.
        """
        raise NotImplementedError

    @abstractmethod
    def render_state(self, pos: Position, canvas: Canvas) -> None:
        """Render the current game position into a canvas.

        Args:
            pos: Current game position that must be represented by the view.
            canvas: Target canvas abstraction where state should be rendered.

        Returns:
            None.
        """
        raise NotImplementedError

    @abstractmethod
    def capture_input(self, *args: Any) -> Movement:
        """Capture user input and convert it to a movement.

        Args:
            *args: Frontend-specific input context required to derive a movement.

        Returns:
            Movement selected or constructed from the provided input context.
        """
        raise NotImplementedError
