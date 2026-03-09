"""Declares an arena behavior that executes turns through player workers."""

from __future__ import annotations

from iarena.arening.behaviors.ConfiguredArenaBase import ConfiguredArenaBase
from iarena.utilizing.timing.Worker import Worker
from iarena.visualizing.terminal_frontend.TerminalView import TerminalView


class WorkerExecuteTurnArena(ConfiguredArenaBase):
    """Arena behavior implementing full turn execution with per-turn timeout."""

    def _execute_turn(self) -> None:
        """Execute one complete turn for the player indicated by the position.

        Returns:
            None.
        """
        current_index = int(self._position.next_player())
        if current_index < 0 or current_index >= len(self._players):
            raise IndexError("Position returned a player index outside configured players range.")

        player = self._players[current_index]
        play_method = getattr(player, "play", None)
        if not callable(play_method):
            raise TypeError("Player must expose a callable `play(position)` method.")

        if isinstance(self._view, TerminalView):
            section_line = "=" * 72
            self._view.output_fnc(section_line)
            self._view.output_fnc(f"STATE START · TURN {self._turn_count + 1}")
            self._view.output_fnc(section_line)
            self._view.render_state(self._position, object())
            self._view.output_fnc(section_line)
            self._view.output_fnc("STATE END")
            self._view.output_fnc(section_line)

        if self._max_turn_time_s is None:
            movement = play_method(self._position)
        else:
            try:
                movement = Worker.limited_time_call(play_method, self._max_turn_time_s, self._position)
            except TimeoutError:
                self._timed_out = True
                return

        self._position = self._rules.next_position(self._position, movement)
        self._last_movement = movement
        self._turn_count += 1
