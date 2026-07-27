"""Abstract base class for algorithm-driven players."""

from iarena.player.Player import Player


class AutomaticPlayer(Player):
    """Marker base class for players that choose moves algorithmically.

    AutomaticPlayer requires no interface or view — it operates purely
    on the game state.  Concrete subclasses implement choose_move with
    a search algorithm, policy network, rule-based system, or any
    other automatic strategy.
    """
