"""Declares the streamlit visualization contract for the Hanoi game."""
# pylint: disable=too-many-lines  # TODO: review

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

from iarena.gaming.hanoi.HanoiMovement import HanoiMovement
from iarena.gaming.hanoi.HanoiPosition import HanoiPosition
from iarena.gaming.hanoi.HanoiRules import HanoiRules


class HanoiStreamlitView(StreamlitView):
    """Concrete streamlit view implementation for the Hanoi game.

    Purpose:
        Provides web UI rendering and interaction bindings for Hanoi in streamlit apps.
    How it works:
        Maps Hanoi rules/position data to streamlit widgets and parses user interactions.
    Used for:
        Browser-based Hanoi gameplay and interactive educational demonstrations.
    Public Attributes:
        Inherits common view behavior from `StreamlitView`.
    """

    def _emit_text(self, canvas: object, text: str) -> None:
        """Write text to a streamlit-like container when supported.

        Args:
            canvas: Candidate streamlit container object.
            text: Text payload to display in the container.

        Returns:
            None.
        """
        writer = getattr(canvas, "write", None)
        if callable(writer):
            writer(text)
            return

        markdown = getattr(canvas, "markdown", None)
        if callable(markdown):
            markdown(text)
            return

        text_writer = getattr(canvas, "text", None)
        if callable(text_writer):
            text_writer(text)

    def _emit_markdown(self, canvas: object, text: str, *, unsafe: bool = False) -> None:
        """Write markdown content to a streamlit-like container when supported.

        Args:
            canvas: Candidate streamlit container object.
            text: Markdown payload to display.
            unsafe: Whether to allow unsafe HTML rendering when backend supports it.

        Returns:
            None.
        """
        markdown = getattr(canvas, "markdown", None)
        if callable(markdown):
            try:
                markdown(text, unsafe_allow_html=unsafe)
                return
            except TypeError:
                markdown(text)
                return

        self._emit_text(canvas, text)

    def _state_lines(self, position: HanoiPosition) -> list[str]:
        """Build human-readable lines describing one Hanoi position.

        Args:
            position: Hanoi position to describe.

        Returns:
            Ordered list of display lines for this position.
        """
        pegs: list[list[int]] = [[] for _ in range(position.n_pegs)]
        for disk_index, peg in enumerate(position.disks):
            pegs[peg].append(disk_index)

        lines = [f"Steps: {position.steps}"]
        lines.extend(f"Peg {idx}: {stack}" for idx, stack in enumerate(pegs))
        return lines

    def _disk_stacks(self, position: HanoiPosition) -> list[list[int]]:
        """Build one per-peg stack of disk sizes from largest (bottom) to smallest (top).

        Args:
            position: Hanoi position used to build stacks.

        Returns:
            list[list[int]]: Disk sizes grouped by peg.
        """
        n_disks = len(position.disks)
        stacks: list[list[int]] = [[] for _ in range(position.n_pegs)]
        for disk_index, peg in enumerate(position.disks):
            stacks[peg].append(n_disks - disk_index)
        return stacks

    def _disk_color(self, size: int, max_size: int) -> str:
        """Return one disk color based on disk size.

        Args:
            size: Disk size to color.
            max_size: Maximum disk size in the current puzzle.

        Returns:
            str: CSS color string in `hsl()` format.
        """
        if max_size <= 1:
            return "hsl(210, 75%, 54%)"
        ratio = (size - 1) / (max_size - 1)
        hue = int(205 - (120 * ratio))
        return f"hsl({hue}, 82%, 55%)"

    def _render_board_html(self, position: HanoiPosition) -> str:
        """Build one HTML board representation for the current Hanoi position.

        Args:
            position: Position to render as a visual board.

        Returns:
            str: HTML payload including inline styles and board markup.
        """
        stacks = self._disk_stacks(position)
        n_disks = len(position.disks)
        levels = max(1, n_disks)
        max_size = max(1, n_disks)
        goal_peg = position.n_pegs - 1
        disks_on_goal = sum(1 for peg in position.disks if peg == goal_peg)

        peg_markup_parts: list[str] = []
        for peg_index, stack in enumerate(stacks):
            level_markup_parts: list[str] = []
            for level in range(levels - 1, -1, -1):
                disk_size = stack[level] if level < len(stack) else 0
                if disk_size == 0:
                    level_markup_parts.append("<div class='ih-level'><div class='ih-empty'></div></div>")
                    continue

                if max_size == 1:
                    disk_width_pct = 82.0
                else:
                    disk_width_pct = 18.0 + ((disk_size - 1) / (max_size - 1)) * 68.0
                disk_color = self._disk_color(disk_size, max_size)
                level_markup_parts.append(
                    (
                        "<div class='ih-level'>"
                        f"<div class='ih-disk' style='width:{disk_width_pct:.1f}%;background:{disk_color};'>"
                        f"{disk_size}"
                        "</div>"
                        "</div>"
                    ),
                )

            peg_markup_parts.append(
                (
                    "<div class='ih-peg'>"
                    "<div class='ih-rod'></div>"
                    f"{''.join(level_markup_parts)}"
                    f"<div class='ih-label'>Peg {peg_index}</div>"
                    "</div>"
                ),
            )

        return (
            "<style>"
            ".ih-wrapper{background:linear-gradient(160deg,#0f172a 0%,#111827 45%,#1f2937 100%);"
            "border-radius:16px;padding:18px 18px 14px 18px;color:#e5e7eb;"
            "box-shadow:0 10px 30px rgba(15,23,42,.30);}"
            ".ih-header{display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;"
            "margin-bottom:14px;font-size:.95rem;font-weight:700;}"
            ".ih-chip{background:rgba(255,255,255,.08);padding:6px 10px;border-radius:999px;}"
            ".ih-board{display:flex;gap:14px;align-items:flex-end;justify-content:space-between;}"
            ".ih-peg{position:relative;flex:1;min-width:86px;background:rgba(15,23,42,.38);"
            "border:1px solid rgba(148,163,184,.30);border-radius:12px;padding:8px 6px 10px 6px;"
            "display:flex;flex-direction:column;justify-content:flex-end;height:250px;overflow:hidden;}"
            ".ih-rod{position:absolute;left:50%;transform:translateX(-50%);bottom:36px;"
            "width:10px;height:185px;background:linear-gradient(180deg,#d1d5db 0%,#9ca3af 100%);"
            "border-radius:999px;opacity:.92;}"
            ".ih-level{position:relative;z-index:2;height:22px;display:flex;align-items:center;justify-content:center;}"
            ".ih-empty{width:6px;height:6px;border-radius:999px;background:rgba(148,163,184,.28);}"
            ".ih-disk{height:18px;border-radius:999px;text-align:center;color:#0b1120;"
            "font-size:.72rem;font-weight:800;line-height:18px;box-shadow:inset 0 -2px 0 rgba(0,0,0,.24),"
            "0 3px 8px rgba(15,23,42,.25);border:1px solid rgba(255,255,255,.44);}"
            ".ih-label{position:relative;z-index:2;margin-top:8px;text-align:center;"
            "font-size:.8rem;font-weight:700;color:#cbd5e1;}"
            "</style>"
            "<div class='ih-wrapper'>"
            "<div class='ih-header'>"
            f"<div class='ih-chip'>Moves: {position.steps}</div>"
            f"<div class='ih-chip'>Goal Progress: {disks_on_goal}/{n_disks}</div>"
            f"<div class='ih-chip'>Goal Peg: {goal_peg}</div>"
            "</div>"
            f"<div class='ih-board'>{''.join(peg_markup_parts)}</div>"
            "</div>"
        )

    def render_info(self, rules: Rules, canvas: Canvas) -> None:
        """Render static or contextual Hanoi information into the streamlit canvas.

        Args:
            rules: Rules object used to compute info text and metadata.
            canvas: Target canvas abstraction where info widgets are rendered.

        Returns:
            None.
        """
        if not isinstance(rules, HanoiRules):
            raise TypeError("rules must be an instance of HanoiRules.")

        conf = rules.configuration
        info = (
            "### Tower of Hanoi\n"
            f"- **Pegs:** `{conf.n_pegs}`\n"
            f"- **Disks:** `{len(conf.disks)}`\n"
            f"- **Goal peg:** `{conf.n_pegs - 1}`\n"
            "- **Rule:** never place a larger disk over a smaller one."
        )
        self._emit_markdown(canvas, info)

    def render_position(self, position: Position, canvas: StreamlitContainer) -> None:
        """Render the current Hanoi board position into the position section.

        Args:
            position: Current game position to display.
            canvas: Streamlit container for the position section.

        Returns:
            None.
        """
        if not isinstance(position, HanoiPosition):
            raise TypeError("position must be an instance of HanoiPosition.")
        self._emit_markdown(canvas, self._render_board_html(position), unsafe=True)

    def render_movements(self, position: Position, canvas: StreamlitContainer) -> None:
        """Render available Hanoi movements into the movement controls section.

        Args:
            position: Current game position used to derive legal movements.
            canvas: Streamlit container for movement controls.

        Returns:
            None.
        """
        if not isinstance(position, HanoiPosition):
            raise TypeError("position must be an instance of HanoiPosition.")

        rules = position.get_rules()
        if not isinstance(rules, HanoiRules):
            raise TypeError("Position rules must be an instance of HanoiRules.")

        moves = [move for move in rules.possible_movements(position) if isinstance(move, HanoiMovement)]
        if not moves:
            self._emit_markdown(canvas, "_No legal movements available._")
            return

        pills = " ".join(
            f"<span style='display:inline-block;padding:4px 8px;margin:2px;"
            "border-radius:999px;background:#e2e8f0;color:#0f172a;font-weight:700;'>"
            f"{move.from_peg} → {move.to_peg}"
            "</span>"
            for move in moves
        )
        self._emit_markdown(canvas, pills, unsafe=True)

    def render_score(self, position: Position, canvas: StreamlitContainer) -> None:
        """Render current Hanoi score information into the score section.

        Args:
            position: Current game position used to compute score data.
            canvas: Streamlit container for score output.

        Returns:
            None.
        """
        if not isinstance(position, HanoiPosition):
            raise TypeError("position must be an instance of HanoiPosition.")

        rules = position.get_rules()
        score = rules.get_score(position).get_score(position.next_player())
        goal_peg = position.n_pegs - 1
        disks_on_goal = sum(1 for peg in position.disks if peg == goal_peg)
        progress = f"{disks_on_goal}/{len(position.disks)}"
        self._emit_markdown(
            canvas,
            (
                "### Position Score\n"
                f"- **Score:** `{float(score):.1f}`\n"
                f"- **Moves:** `{position.steps}`\n"
                f"- **Progress:** `{progress}`"
            ),
        )

    def capture_input(self, state: StreamlitSession) -> Movement:
        """Capture streamlit session interaction state and return one movement.

        Args:
            state: Streamlit session state containing latest user interaction values.

        Returns:
            Movement: Movement extracted from current streamlit UI state.
        """
        from_peg: int | None = None
        to_peg: int | None = None

        if isinstance(state, Mapping):
            raw_from = state.get("from_peg")
            raw_to = state.get("to_peg")
            if raw_from is not None and raw_to is not None:
                from_peg = int(raw_from)
                to_peg = int(raw_to)
        else:
            raw_from = getattr(state, "from_peg", None)
            raw_to = getattr(state, "to_peg", None)
            if raw_from is not None and raw_to is not None:
                from_peg = int(raw_from)
                to_peg = int(raw_to)

        if from_peg is None or to_peg is None:
            raise ValueError("state must contain integer-like 'from_peg' and 'to_peg' values.")

        return HanoiMovement(from_peg=from_peg, to_peg=to_peg)
