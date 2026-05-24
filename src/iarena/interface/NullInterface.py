"""No-op interface for automatic-player-only sessions."""

from iarena.interface.Interface import Interface


class NullInterface(Interface):
    """Interface implementation that discards all output and rejects input.

    Intended for simulations and tests where no human is present.
    All render calls are silently ignored; ask raises NotImplementedError
    because there is no user to provide input.
    """

    def render(self, content: str) -> None:
        """Discard content silently."""

    def ask(self, prompt: str) -> str:
        """Raise NotImplementedError — no user interaction available."""
        raise NotImplementedError("NullInterface does not support user input.")
