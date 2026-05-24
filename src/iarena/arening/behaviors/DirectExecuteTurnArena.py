"""Declares an arena behavior that executes turns without worker threads."""

from __future__ import annotations

from iarena.visualizing.terminal_frontend.TerminalView import TerminalView

from iarena.arening.behaviors.ConfiguredArenaBase import ConfiguredArenaBase


class DirectExecuteTurnArena(ConfiguredArenaBase):
    """Arena behavior implementing in-process turn execution without threading."""

    def _execute_turn(self) -> None:
        """Execute one complete turn by calling the player directly.

        Returns:
            None.
        """
        current_index = int(self._current_position.next_player())
        if current_index < 0 or current_index >= len(self._players):
            raise IndexError("Position returned a player index outside configured players range.")

        player = self._players[current_index]
        play_method = getattr(player, "play", None)
        if not callable(play_method):
            raise TypeError("Player must expose a callable `play(position)` method.")

        if isinstance(self._view, TerminalView):
            # section_line = "=" * 72
            # self._view.output_fnc(section_line)
            # self._view.output_fnc(f"STATE START · TURN {self._turn_count + 1}")
            # self._view.output_fnc(section_line)
            self._view.render_state(self._current_position, object())
            # self._view.output_fnc(section_line)
            # self._view.output_fnc("STATE END")
            # self._view.output_fnc(section_line)

        movement = play_method(self._current_position)
        self._current_position = self._rules.next_position(self._current_position, movement)
        self._last_movement = movement
        self._turn_count += 1
