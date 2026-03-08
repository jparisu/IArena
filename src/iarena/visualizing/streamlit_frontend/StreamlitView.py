"""Declares the abstract streamlit frontend contract for game-specific streamlit views."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules
    from iarena.visualizing.Canvas import Canvas
    from iarena.visualizing.streamlit_frontend.StreamlitSession import StreamlitSession

from iarena.visualizing.streamlit_frontend.StreamlitContainer import StreamlitContainer
from iarena.visualizing.View import View


class StreamlitView(View, ABC):
    """Abstract streamlit frontend contract for game-specific streamlit views.

    Purpose:
        Provides the `StreamlitView` type within the IArena architecture.
    How it works:
        Standardizes streamlit-oriented rendering and input behavior for concrete game frontends.
    Used for:
        Implementing web-based interactive game interfaces with streamlit widgets and panels.
    Public Attributes:
        Inherits shared view attributes from `View`.
    """

    @abstractmethod
    def render_info(self, rules: Rules, canvas: Canvas) -> None:
        """Render streamlit info layer with app-specific widgets.

        Args:
            rules: Rules instance that defines the game mechanics for the current match.
            canvas: Target canvas abstraction associated with streamlit rendering.

        Returns:
            None.
        Raises:
            NotImplementedError: Always, subclasses must implement this method.
        """
        raise NotImplementedError

    def render_state(self, pos: Position, canvas: Canvas) -> None:
        """Render streamlit state layer using default frontend behavior.

        Args:
            pos: Current game position that should be represented in streamlit UI.
            canvas: Target canvas abstraction associated with streamlit rendering.

        Returns:
            None.

        """
        position_canvas, movement_canvas, score_canvas = self._resolve_state_canvases(canvas)
        self.render_position(pos, position_canvas)
        self.render_movements(pos, movement_canvas)
        self.render_score(pos, score_canvas)

    def _resolve_state_canvases(
        self,
        canvas: Canvas,
    ) -> tuple[StreamlitContainer, StreamlitContainer, StreamlitContainer]:
        """Resolve the three streamlit section containers required by `render_state`.

        Args:
            canvas: Canvas input passed to `render_state`.

        Returns:
            Triple with `(position, movements, score)` streamlit containers.

        Raises:
            TypeError: If `canvas` does not provide compatible streamlit containers.
        """
        if isinstance(canvas, StreamlitContainer):
            return canvas, canvas, canvas

        if isinstance(canvas, Mapping):
            return (
                self._coerce_streamlit_container(canvas.get("position"), name="position"),
                self._coerce_streamlit_container(canvas.get("movements"), name="movements"),
                self._coerce_streamlit_container(canvas.get("score"), name="score"),
            )

        return (
            self._coerce_streamlit_container(getattr(canvas, "position", None), name="position"),
            self._coerce_streamlit_container(getattr(canvas, "movements", None), name="movements"),
            self._coerce_streamlit_container(getattr(canvas, "score", None), name="score"),
        )

    def _coerce_streamlit_container(self, candidate: object, *, name: str) -> StreamlitContainer:
        """Validate and return one section container expected by streamlit rendering.

        Args:
            candidate: Candidate object to validate as a `StreamlitContainer`.
            name: Logical section name used for error reporting.

        Returns:
            The validated streamlit container instance.

        Raises:
            TypeError: If `candidate` is not a `StreamlitContainer`.
        """
        if isinstance(candidate, StreamlitContainer):
            return cast(StreamlitContainer, candidate)
        raise TypeError(
            f"Invalid streamlit canvas section '{name}': expected StreamlitContainer, got {type(candidate).__name__}."
        )

    @abstractmethod
    def render_position(self, position: Position, canvas: StreamlitContainer) -> None:
        """Render the current position section in streamlit.

        Args:
            position: Current game position to display in the position panel.
            canvas: Streamlit container used to render the position section.

        Returns:
            None.
        Raises:
            NotImplementedError: Always, subclasses must implement this method.
        """
        raise NotImplementedError

    @abstractmethod
    def render_movements(self, position: Position, canvas: StreamlitContainer) -> None:
        """Render available movements section in streamlit.

        Args:
            position: Current game position used to compute available movements.
            canvas: Streamlit container used to render movement controls.

        Returns:
            None.
        Raises:
            NotImplementedError: Always, subclasses must implement this method.
        """
        raise NotImplementedError

    @abstractmethod
    def render_score(self, position: Position, canvas: StreamlitContainer) -> None:
        """Render score section in streamlit.

        Args:
            position: Current game position used to derive scoreboard information.
            canvas: Streamlit container used to render score output.

        Returns:
            None.
        Raises:
            NotImplementedError: Always, subclasses must implement this method.
        """
        raise NotImplementedError

    @abstractmethod
    def capture_input(self, state: StreamlitSession) -> Movement:
        """Capture streamlit UI state and convert it into a movement.

        Args:
            state: Streamlit session object containing user interaction state.

        Returns:
            Movement selected or constructed from the streamlit session state.
        Raises:
            NotImplementedError: Always, subclasses must implement this method.
        """
        raise NotImplementedError
