"""Declares a generic one-player shortest-path strategy based on Dijkstra search."""

from __future__ import annotations

from abc import ABC, abstractmethod
from heapq import heappop, heappush
from typing import TYPE_CHECKING

from iarena.playing.Player import Player

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules
    from iarena.playing.PlayerIndex import PlayerIndex


class DijkstraPlayer(Player, ABC):
    """Abstract one-player strategy that follows a lowest-cost path to completion.

    Purpose:
        Provide a reusable shortest-path player for single-player deterministic games.
    How it works:
        Runs Dijkstra search over legal movements from the current position and returns
        the first movement of one minimal-cost path to any finished position.
    Used for:
        Building game-specific optimal players by only defining how position cost is measured.
    Public Attributes:
        None declared at class level in this base definition.
    """

    def __init__(self, name: str | None = None) -> None:
        """Initialize the player with an optional name.

        Args:
            name (str | None): Optional name for the player. If None, a default name is assigned.

        Returns:
            None.
        """
        super().__init__(name=name)
        self._rules: Rules | None = None
        self._player_index: PlayerIndex | None = None

    def name(self) -> str:
        """Return the canonical identifier for this generic player family.

        Returns:
            str: Stable player type identifier.
        """
        return "dijkstra-player"

    @abstractmethod
    def current_cost(self, pos: Position) -> float:
        """Return the cumulative cost of reaching the provided position.

        Args:
            pos: Position whose cumulative cost value must be returned.

        Returns:
            float: Cumulative cost associated with `pos`.
        """
        raise NotImplementedError

    def _reconstruct_first_movement(
        self,
        start_hash: int,
        goal_hash: int,
        parents: dict[int, tuple[int, Movement]],
    ) -> Movement:
        """Return the first movement of the path from `start_hash` to `goal_hash`.

        Args:
            start_hash: Hash of the position where search started.
            goal_hash: Hash of one reached finished position.
            parents: Parent mapping of child hash to `(parent_hash, movement)`.

        Returns:
            Movement: First movement from the start position to the chosen goal path.
        """
        if goal_hash == start_hash:
            raise ValueError("No movement available: the game is already solved.")

        trace_hash = goal_hash
        while True:
            if trace_hash not in parents:
                raise ValueError("Could not reconstruct a movement path from the searched positions.")

            parent_hash, movement = parents[trace_hash]
            if parent_hash == start_hash:
                return movement
            trace_hash = parent_hash

    def _compute_next_movement(self, pos: Position) -> Movement:
        """Compute one lowest-cost movement from the given position.

        Args:
            pos: Current game position where the player must act.

        Returns:
            Movement: First movement along one minimum-cost path to completion.
        """
        rules = pos.get_rules()
        if rules.n_players() != 1:
            raise ValueError("DijkstraPlayer can only be used with one-player games.")
        if rules.is_finished(pos):
            raise ValueError("No movement available: the game is already solved.")

        start_hash = pos.hash()
        start_cost = self.current_cost(pos)
        frontier: list[tuple[float, int, Position]] = [(start_cost, 0, pos)]
        best_cost_by_hash: dict[int, float] = {start_hash: start_cost}
        parents: dict[int, tuple[int, Movement]] = {}
        pushed_nodes = 1

        while frontier:
            popped_cost, _, current_position = heappop(frontier)
            current_hash = current_position.hash()
            known_cost = best_cost_by_hash.get(current_hash)
            if known_cost is None or popped_cost > known_cost:
                continue

            if rules.is_finished(current_position):
                return self._reconstruct_first_movement(start_hash=start_hash, goal_hash=current_hash, parents=parents)

            for movement in rules.possible_movements(current_position):
                next_position = rules.next_position(current_position, movement)
                next_hash = next_position.hash()
                next_cost = self.current_cost(next_position)

                if next_cost < popped_cost:
                    raise ValueError("DijkstraPlayer requires non-decreasing cumulative costs along legal movements.")

                previous_cost = best_cost_by_hash.get(next_hash)
                if previous_cost is not None and next_cost >= previous_cost:
                    continue

                best_cost_by_hash[next_hash] = next_cost
                parents[next_hash] = (current_hash, movement)
                heappush(frontier, (next_cost, pushed_nodes, next_position))
                pushed_nodes += 1

        raise ValueError("Could not compute a path to a finished position.")

    def play(self, pos: Position) -> Movement:
        """Choose and return the next movement for the provided position.

        Args:
            pos: Current position where the player must act.

        Returns:
            Movement: Movement selected by Dijkstra shortest-path search.
        """
        return self._compute_next_movement(pos)

    def starting_game(self, rules: Rules, player_index: PlayerIndex) -> None:
        """Initialize runtime context for a newly started one-player game.

        Args:
            rules: Rules object associated with the game to be played.
            player_index: Index assigned to this player in the arena.

        Returns:
            None.
        """
        if rules.n_players() != 1:
            raise ValueError("DijkstraPlayer requires one-player rules.")
        self._rules = rules
        self._player_index = player_index
