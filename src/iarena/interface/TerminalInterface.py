"""Terminal (stdin/stdout) interface for interactive game sessions."""

from __future__ import annotations

from typing import Any

from iarena.game.GameMove import GameMove
from iarena.game.GameState import GameState
from iarena.interface.Interface import Interface
from iarena.view.View import View

if True:  # TYPE_CHECKING guard not needed here — imported for isinstance only
    pass


class TerminalInterface(Interface):
    """Interface that reads from stdin and writes to stdout.

    Suitable for local human play in a terminal. Lifecycle hooks print
    human-readable banners and result messages.

    Parameters
    ----------
    view:
        Game-specific view used to render state at the start of each turn.
        May be None for automatic-only sessions.
    """

    def __init__(self, view: View | None = None) -> None:
        super().__init__(view)

    # ------------------------------------------------------------------
    # Low-level I/O
    # ------------------------------------------------------------------

    def render(self, content: str) -> None:
        """Print content to stdout."""
        print(content)

    def ask(self, prompt: str) -> str:
        """Print prompt and return the line entered by the user."""
        return input(prompt)

    # ------------------------------------------------------------------
    # Lifecycle hooks
    # ------------------------------------------------------------------

    def on_game_start(self, state: GameState) -> None:
        print("=" * 30)
        print("        Welcome to IArena!")
        print("=" * 30)

    def on_turn_start(self, state: GameState, player: Any) -> None:
        print()
        super().on_turn_start(state, player)

    def on_invalid_move(self, state: GameState, player: Any, move: GameMove) -> None:
        print(f"Move {move} is not legal — cell may already be occupied. Please try again.")

    def on_turn_end(self, state: GameState, player: Any, move: GameMove) -> None:
        print("-" * 30)

    def on_game_end(self, state: GameState, result: Any) -> None:
        print()
        print("=" * 30)
        if result is None:
            print("        It's a draw!")
        else:
            print(f"      Player {result + 1} wins!")
        print("=" * 30)
