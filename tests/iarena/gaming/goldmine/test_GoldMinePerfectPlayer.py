"""Tests for the GoldMine perfect-player implementation."""

from __future__ import annotations

from iarena.gaming.goldmine.GoldMineConfiguration import GoldMineConfiguration
from iarena.gaming.goldmine.GoldMinePerfectPlayer import GoldMinePerfectPlayer
from iarena.gaming.goldmine.GoldMineRules import GoldMineRules
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate


def _rules() -> GoldMineRules:
    """Return one deterministic GoldMine ruleset with all hints enabled."""
    return GoldMineRules(
        GoldMineConfiguration(
            n_rows=3,
            n_cols=3,
            start=SquareMapCoordinate(0, 0),
            target=SquareMapCoordinate(2, 2),
            map_data=[
                [0.0, 1.0, 9.0],
                [1.0, 1.0, 9.0],
                [9.0, 1.0, 1.0],
            ],
            heuristic_map_data=[
                [0.6, 0.5, 0.4],
                [0.5, 0.4, 0.3],
                [0.4, 0.3, 0.2],
            ],
            compass_activated=True,
            proximity_activated=True,
            density_activated=True,
            seed=7,
        ),
    )


def test_name_returns_stable_identifier() -> None:
    """`name` should return the canonical GoldMine perfect-player id."""
    player = GoldMinePerfectPlayer()

    assert player.name() == "goldmine-perfect"


def test_starting_game_stores_runtime_context() -> None:
    """`starting_game` should keep rules and player index runtime references."""
    player = GoldMinePerfectPlayer()
    rules = _rules()

    player.starting_game(rules=rules, player_index=PlayerIndex(0))

    assert player._rules is rules
    assert player._player_index == PlayerIndex(0)
    assert player._current_coordinate == SquareMapCoordinate(0, 0)


def test_play_returns_legal_movement() -> None:
    """`play` should always return one legal movement for the provided position."""
    player = GoldMinePerfectPlayer(seed=1)
    rules = _rules()
    player.starting_game(rules=rules, player_index=PlayerIndex(0))
    position = rules.first_position()

    movement = player.play(position)

    legal_directions = {candidate.direction for candidate in rules.possible_movements(position)}
    assert movement.direction in legal_directions


def test_play_records_compass_and_proximity_readings() -> None:
    """`play` should store available compass and proximity readings per visited tile."""
    player = GoldMinePerfectPlayer(seed=3)
    rules = _rules()
    player.starting_game(rules=rules, player_index=PlayerIndex(0))
    position = rules.first_position()

    first_movement = player.play(position)
    next_position = rules.next_position(position, first_movement)
    player.play(next_position)

    assert (0, 0) in player._compass_readings
    assert len(player._proximity_readings) >= 2
    assert player._estimated_target is not None


def test_play_updates_known_neighbor_costs() -> None:
    """`play` should update the internal known-cost map from local movement costs."""
    player = GoldMinePerfectPlayer(seed=5)
    rules = _rules()
    player.starting_game(rules=rules, player_index=PlayerIndex(0))
    position = rules.first_position()

    player.play(position)

    assert player._known_tile_costs[(0, 1)] == 1.0
    assert player._known_tile_costs[(1, 0)] == 1.0
