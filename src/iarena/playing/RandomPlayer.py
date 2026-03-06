"""Random player implementation that samples legal movements uniformly."""

from __future__ import annotations

from iarena.desining.gaming.GameRules import GameRules
from iarena.desining.gaming.Movement import Movement
from iarena.desining.gaming.Position import Position
from iarena.desining.playing.Player import Player, PlayerIndex
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


class RandomPlayer(Player):
    """Player that picks one legal movement uniformly at random."""

    def __init__(
        self,
        random_generator: RandomGenerator | None = None,
        seed: int | None = None,
        name: str | None = None,
    ) -> None:
        """Initialize a random player.

        Args:
            random_generator: Optional random generator to control sampling.
            seed: Optional seed used when a generator is not provided.
            name: Optional display name for this player.

        Returns:
            None.
        """
        if random_generator is not None and seed is not None:
            raise ValueError("provide either random_generator or seed, not both")
        super().__init__(name=name)
        self._rules: GameRules | None = None
        self._random_generator = random_generator if random_generator is not None else RandomGenerator(seed=seed)

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
        """Choose one legal movement uniformly at random.

        Args:
            position: Current game position.

        Returns:
            Randomly selected legal movement.
        """
        if self._rules is None:
            raise RuntimeError("RandomPlayer requires starting_game() before play()")

        movements = list(self._rules.possible_movements(position))
        if not movements:
            raise RuntimeError("no legal movement available for RandomPlayer")

        return self._random_generator.choice(movements)
