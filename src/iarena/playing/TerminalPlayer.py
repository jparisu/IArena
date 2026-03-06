"""Terminal-interactive player implementation for any IArena game."""

from __future__ import annotations

from collections.abc import Callable

from iarena.desining.gaming.GameRules import GameRules
from iarena.desining.gaming.Movement import Movement
from iarena.desining.gaming.Position import Position
from iarena.desining.playing.Player import Player, PlayerIndex
from iarena.desining.visualing.TerminalGame import TerminalGame

InputFunction = Callable[[str], str]
OutputFunction = Callable[[str], object]


class TerminalPlayer(Player):
    """Human-controlled player that picks movements from terminal prompts."""

    def __init__(
        self,
        input_function: InputFunction = input,
        output_function: OutputFunction = print,
        name: str | None = None,
    ) -> None:
        """Initialize a terminal-interactive player.

        Args:
            input_function: Function used to receive user input from terminal.
            output_function: Function used to write messages to terminal.
            name: Optional display name for this player.

        Returns:
            None.
        """
        super().__init__(name=name)
        self._rules: GameRules | None = None
        self._input_function = input_function
        self._output_function = output_function

    def starting_game(self, rules: GameRules, player_index: PlayerIndex) -> None:
        """Store rules reference before the game starts.

        Args:
            rules: Rules object that governs the game.
            player_index: Index assigned to this player.

        Returns:
            None.
        """
        del player_index
        self._rules = rules

    def play(self, position: Position) -> Movement:
        """Request one movement by prompting in the terminal.

        Args:
            position: Current game position.

        Returns:
            Movement selected by the user in terminal.
        """
        return self.play_from_terminal(position)

    def play_from_terminal(self, position: Position) -> Movement:
        """Request one movement by prompting in the terminal.

        Args:
            position: Current game position.

        Returns:
            Movement selected by the user in terminal.
        """
        if self._rules is None:
            raise RuntimeError("TerminalPlayer requires starting_game() before play_from_terminal()")

        movements = list(self._rules.possible_movements(position))
        if not movements:
            raise RuntimeError("no legal movement available for TerminalPlayer")

        terminal_rules = self._rules if isinstance(self._rules, TerminalGame) else None

        self._output_function("Possible movements:")
        for index, movement in enumerate(movements, start=1):
            movement_text = (
                terminal_rules.movement_to_terminal(movement) if terminal_rules is not None else str(movement)
            )
            self._output_function(f"{index}. {movement_text}")

        while True:
            raw_choice = self._input_function("Choose movement number: ").strip()
            if terminal_rules is not None:
                try:
                    return terminal_rules.movement_from_terminal(raw_choice, movements)
                except ValueError:
                    self._output_function(f"Invalid movement. Enter a valid option between 1 and {len(movements)}.")
                    continue

            try:
                movement_index = int(raw_choice)
            except ValueError:
                self._output_function(f"Invalid movement. Enter an integer between 1 and {len(movements)}.")
                continue

            if 1 <= movement_index <= len(movements):
                return movements[movement_index - 1]

            self._output_function(f"Invalid movement. Enter an integer between 1 and {len(movements)}.")
