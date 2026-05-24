"""Defines a generic random player implementation placeholder."""

from __future__ import annotations

from typing import TYPE_CHECKING

from iarena.playing.Player import Player
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules
    from iarena.playing.PlayerIndex import PlayerIndex
    from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


class PolyvalentRandomPlayer(Player):
    """Generic player that selects movements uniformly at random for any game.

    Purpose:
        Provides the `PolyvalentRandomPlayer` type within the IArena architecture.
    How it works:
        Encapsulates behavior through its public API and type contracts defined in this class body.
    Used for:
        Building game, mapping, utility, or protocol components that can be composed by other modules.
    Public Attributes:
        rng (RandomGenerator): Public attribute exposed by this class.
    """

    rng: RandomGenerator

    def __init__(
        self,
        name: str = "polyvalent-random",
        rng: RandomGenerator | None = None,
        seed: int | None = None,
    ) -> None:
        """Initialize a new random player instance with optional name and RNG configuration.

        Args:
            name (str): Optional name for this player instance. Defaults to "polyvalent-random".
            rng (RandomGenerator | None): Optional custom random generator. If None, a new one is created.
            seed (int | None): Optional seed for RNG initialization. Ignored if `rng` is provided.

        Returns:
            None: This constructor initializes the player instance and does not return a value.
        """
        self._name = name
        self._seed = seed
        self.rng = rng if rng is not None else RandomGenerator(seed=seed)

    def name(self) -> str:
        """Return a stable identifier for this random player type.

        What it does:
            Exposes the recognizable name required by the player protocol.
        How it works:
            Placeholder method for subclasses or future concrete implementation.
        Args:
            None.
        Returns:
            str: Canonical random-player identifier.
        """
        return self._name

    def play(self, pos: Position) -> Movement:
        """Choose and return the next movement for the given position.

        What it does:
            Defines the movement-selection operation based on random choice.
        How it works:
            Placeholder method to be implemented using available legal moves.
        Args:
            pos (Position): Current game position where this player must act.
        Returns:
            Movement: Movement selected by the random strategy.
        """
        rules = pos.get_rules()
        possible_movements = list(rules.possible_movements(pos))
        if not possible_movements:
            raise ValueError("No legal movements available for PolyvalentRandomPlayer.")
        return self.rng.choice(possible_movements)

    def starting_game(self, rules: Rules, player_index: PlayerIndex) -> None:
        """Initialize runtime state before the first turn of a game.

        What it does:
            Defines the setup operation invoked at game start.
        How it works:
            Placeholder method for preparing RNG and match context.
        Args:
            rules (Rules): Rules object that governs the upcoming game.
            player_index (PlayerIndex): Index assigned to this player.
        Returns:
            None: This hook performs setup side effects only.
        """
        self._rules = rules
        self._player_index = player_index
        self.rng = RandomGenerator(self._seed)
