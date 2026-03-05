"""Marker interface for game actions.

Concrete games should define one or more movement classes carrying the exact
payload needed by `IGameRules.next_position` to transition state.
"""


class IMovement:
    """Base movement type for all game-specific actions.

    The interface is intentionally empty: movement structure is fully defined by
    concrete games.
    """
