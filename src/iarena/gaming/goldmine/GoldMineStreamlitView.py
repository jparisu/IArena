"""Declares the streamlit visualization contract for the GoldMine game."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from iarena.visualizing.streamlit_frontend.StreamlitView import StreamlitView

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules
    from iarena.visualizing.Canvas import Canvas
    from iarena.visualizing.streamlit_frontend.StreamlitContainer import StreamlitContainer
    from iarena.visualizing.streamlit_frontend.StreamlitSession import StreamlitSession

from iarena.gaming.goldmine.GoldMineMovement import GoldMineMovement
from iarena.gaming.goldmine.GoldMinePosition import GoldMinePosition
from iarena.gaming.goldmine.GoldMineRules import GoldMineRules
from iarena.utilizing.mapping.square_map.SquareMapDirection import SquareMapDirection


class GoldMineStreamlitView(StreamlitView):
    """Concrete streamlit view implementation for the GoldMine game.

    Purpose:
        Provides web UI rendering and interaction bindings for GoldMine in streamlit apps.
    How it works:
        Renders only player-visible state: movement options and enabled heuristics.
    Used for:
        Browser-based GoldMine gameplay with directional movement controls.
    Public Attributes:
        Inherits common view behavior from `StreamlitView`.
    """

    def _emit_markdown(self, canvas: object, text: str) -> None:
        """Write markdown content to a streamlit-like container when supported.

        Args:
            canvas: Candidate streamlit container object.
            text: Markdown payload to display.

        Returns:
            None.
        """
        markdown = getattr(canvas, "markdown", None)
        if callable(markdown):
            markdown(text)
            return

        writer = getattr(canvas, "write", None)
        if callable(writer):
            writer(text)

    def _emit_html(self, canvas: object, html: str) -> None:
        """Write HTML content to a streamlit-like container when supported.

        Args:
            canvas: Candidate streamlit container object.
            html: HTML payload to display.

        Returns:
            None.
        """
        markdown = getattr(canvas, "markdown", None)
        if callable(markdown):
            markdown(html, unsafe_allow_html=True)
            return

        self._emit_markdown(canvas, html)

    def _direction_label(self, direction: SquareMapDirection) -> str:
        """Return UI label for one cardinal direction.

        Args:
            direction: Direction enum value.

        Returns:
            str: UI-friendly direction text.
        """
        return direction.name

    def _render_hint_panel(self, position: GoldMinePosition, canvas: object) -> None:
        """Render active GoldMine hints as a styled card panel.

        Args:
            position: Current game position.
            canvas: Streamlit-like container where hints are rendered.

        Returns:
            None.
        """
        hint_items: list[tuple[str, str]] = []

        rules = position.get_rules()
        if not isinstance(rules, GoldMineRules):
            raise TypeError("Position rules must be an instance of GoldMineRules.")

        if rules._configuration.compass_activated:
            hint_items.append(("Compass", position.get_compass().name))
        if rules._configuration.proximity_activated:
            hint_items.append(("Proximity", str(position.get_proximity())))
        if rules._configuration.density_activated:
            hint_items.append(("Density", f"{position.get_density():.3f}"))

        if not hint_items:
            return

        cards_html = "".join(
            (
                "<div style='flex: 1 1 150px; min-width: 140px; border: 1px solid #d9e2ec; "
                "border-radius: 12px; padding: 10px 12px; background: linear-gradient(180deg, #f7fbff 0%, #edf5ff 100%);'>"
                f"<div style='font-size: 0.78rem; color: #486581; letter-spacing: 0.04em; text-transform: uppercase;'>{label}</div>"
                f"<div style='font-size: 1.05rem; font-weight: 700; color: #102a43; margin-top: 4px;'>{value}</div>"
                "</div>"
            )
            for label, value in hint_items
        )
        panel_html = (
            "<div style='margin-top: 10px;'>"
            "<div style='font-size: 0.82rem; font-weight: 700; color: #334e68; margin-bottom: 8px; letter-spacing: 0.04em; "
            "text-transform: uppercase;'>Heuristic Signals</div>"
            "<div style='display: flex; gap: 10px; flex-wrap: wrap;'>"
            f"{cards_html}"
            "</div>"
            "</div>"
        )
        self._emit_html(canvas, panel_html)

    def _emit_pyplot(self, canvas: object, figure: object) -> None:
        """Render a matplotlib figure on a streamlit-like container when supported.

        Args:
            canvas: Candidate streamlit container object.
            figure: Matplotlib figure object to render.

        Returns:
            None.
        """
        pyplot = getattr(canvas, "pyplot", None)
        if callable(pyplot):
            try:
                pyplot(figure, use_container_width=True)
            except TypeError:
                pyplot(figure)
            return

        import streamlit as st

        st.pyplot(figure, use_container_width=True)

    def _render_debug_map_section(self, position: GoldMinePosition, canvas: StreamlitContainer) -> None:
        """Render a hidden-by-default debug section with the full map plot.

        Args:
            position: Current game position.
            canvas: Streamlit container where the section is rendered.

        Returns:
            None.
        """
        rules = position.get_rules()
        if not isinstance(rules, GoldMineRules):
            raise TypeError("Position rules must be an instance of GoldMineRules.")

        native_canvas = canvas.container
        if native_canvas is None:
            return

        expander = getattr(native_canvas, "expander", None)
        if not callable(expander):
            return

        import matplotlib.pyplot as plt

        figure = rules._generate_plot_position(position)
        with expander("Debug map (hidden information)", expanded=False) as debug_canvas:
            self._emit_pyplot(debug_canvas, figure)
        plt.close(figure)

    def render_info(self, rules: Rules, canvas: Canvas) -> None:
        """Render static GoldMine information into the streamlit canvas.

        Args:
            rules: Rules object used to compute info text and metadata.
            canvas: Target canvas abstraction where info widgets are rendered.

        Returns:
            None.
        """
        if not isinstance(rules, GoldMineRules):
            raise TypeError("rules must be an instance of GoldMineRules.")

        conf = rules._configuration
        info = (
            "### GoldMine\n"
            f"- **Map size:** `{conf.n_rows}x{conf.n_cols}`\n"
            "- **Goal:** Reach the hidden gold minimizing accumulated cost.\n"
            "- **Controls:** Use directional buttons (`UP`, `DOWN`, `LEFT`, `RIGHT`)."
        )
        self._emit_markdown(canvas, info)

    def render_position(self, position: Position, canvas: StreamlitContainer) -> None:
        """Render the current GoldMine state into the position section.

        Args:
            position: Current game position to display.
            canvas: Streamlit container for the position section.

        Returns:
            None.
        """
        if not isinstance(position, GoldMinePosition):
            raise TypeError("position must be an instance of GoldMinePosition.")

        self._emit_markdown(
            canvas,
            (
                "### Exploration\n"
                "- **Known information:** possible movements and active heuristic signals."
            ),
        )
        self._render_hint_panel(position, canvas)
        self._render_debug_map_section(position, canvas)

    def _render_direction_button(
        self,
        direction: SquareMapDirection,
        legal_movements: dict[SquareMapDirection, GoldMineMovement],
        position: GoldMinePosition,
        *,
        key: str,
        container: object,
    ) -> None:
        """Render one direction button with movement cost and click behavior.

        Args:
            direction: Direction rendered by the button.
            legal_movements: Mapping of currently legal direction movements.
            position: Current GoldMine position used to compute costs.
            key: Unique streamlit key for the button.
            container: Streamlit-like container where the button is rendered.

        Returns:
            None.
        """
        import streamlit as st

        is_legal = direction in legal_movements
        cost = position.get_cost_from_direction(direction) if is_legal else None
        label = self._direction_label(direction)
        if cost is not None:
            label = f"{label}\n(cost {cost:.2f})"

        clicked = container.button(
            label,
            key=key,
            disabled=not is_legal,
            use_container_width=True,
        )
        if clicked:
            st.session_state["selected_movement"] = legal_movements[direction]

    def render_movements(self, position: Position, canvas: StreamlitContainer) -> None:
        """Render available GoldMine movements into the movement controls section.

        Args:
            position: Current game position used to derive legal movements.
            canvas: Streamlit container for movement controls.

        Returns:
            None.
        """
        if not isinstance(position, GoldMinePosition):
            raise TypeError("position must be an instance of GoldMinePosition.")

        rules = position.get_rules()
        if not isinstance(rules, GoldMineRules):
            raise TypeError("Position rules must be an instance of GoldMineRules.")

        legal_movements = {
            movement.direction: movement
            for movement in rules.possible_movements(position)
            if isinstance(movement, GoldMineMovement)
        }

        import streamlit as st

        native_canvas = canvas.container if canvas.container is not None else st.container()
        with native_canvas:
            top_left, top_center, top_right = st.columns(3)
            self._render_direction_button(
                SquareMapDirection.UP,
                legal_movements,
                position,
                key=f"goldmine_move_{position.hash()}_up",
                container=top_center,
            )

            mid_left, mid_center, mid_right = st.columns(3)
            self._render_direction_button(
                SquareMapDirection.LEFT,
                legal_movements,
                position,
                key=f"goldmine_move_{position.hash()}_left",
                container=mid_left,
            )
            mid_center.markdown("**Current**")
            self._render_direction_button(
                SquareMapDirection.RIGHT,
                legal_movements,
                position,
                key=f"goldmine_move_{position.hash()}_right",
                container=mid_right,
            )

            bottom_left, bottom_center, bottom_right = st.columns(3)
            self._render_direction_button(
                SquareMapDirection.DOWN,
                legal_movements,
                position,
                key=f"goldmine_move_{position.hash()}_down",
                container=bottom_center,
            )

    def render_score(self, position: Position, canvas: StreamlitContainer) -> None:
        """Render current GoldMine score into the score section.

        Args:
            position: Current game position used to compute score data.
            canvas: Streamlit container for score output.

        Returns:
            None.
        """
        if not isinstance(position, GoldMinePosition):
            raise TypeError("position must be an instance of GoldMinePosition.")

        rules = position.get_rules()
        if not isinstance(rules, GoldMineRules):
            raise TypeError("Position rules must be an instance of GoldMineRules.")

        score = float(rules.get_score(position).get_score(position.next_player()))
        accumulated_cost = -score

        lines = [
            "### Position Score",
            f"- **Score:** `{score:.2f}`",
            f"- **Accumulated cost:** `{accumulated_cost:.2f}`",
        ]

        self._emit_markdown(canvas, "\n".join(lines))

    def capture_input(self, state: StreamlitSession) -> Movement:
        """Capture streamlit session interaction state and return one movement.

        Args:
            state: Streamlit session state containing latest user interaction values.

        Returns:
            Movement: Movement extracted from current streamlit UI state.
        """
        raw_direction: object | None = None

        if isinstance(state, Mapping):
            raw_direction = state.get("goldmine_direction")
        else:
            raw_direction = getattr(state, "goldmine_direction", None)

        if raw_direction is None:
            raise ValueError("state must contain 'goldmine_direction' value.")

        if isinstance(raw_direction, SquareMapDirection):
            direction = raw_direction
        else:
            direction = SquareMapDirection[str(raw_direction)]

        return GoldMineMovement(direction=direction)
