"""Tests for the Hanoi optimal player implementation."""

from __future__ import annotations

from iarena.gaming.hanoi.HanoiConfiguration import HanoiConfiguration
from iarena.gaming.hanoi.HanoiPerfectPlayer import HanoiPerfectPlayer
from iarena.gaming.hanoi.HanoiPosition import HanoiPosition
from iarena.gaming.hanoi.HanoiRules import HanoiRules
from iarena.playing.PlayerIndex import PlayerIndex


def test_name_returns_stable_identifier() -> None:
    player = HanoiPerfectPlayer()

    assert player.name() == "hanoi-perfect"


def test_play_returns_legal_move_towards_solution() -> None:
    player = HanoiPerfectPlayer()
    rules = HanoiRules(HanoiConfiguration(n_pegs=3, disks=[0, 0, 0]))
    position = rules.first_position()

    movement = player.play(position)

    assert (movement.from_peg, movement.to_peg) in {(0, 1), (0, 2)}


def test_starting_game_stores_runtime_context() -> None:
    player = HanoiPerfectPlayer()
    rules = HanoiRules(HanoiConfiguration(n_pegs=3, disks=[0, 0]))

    player.starting_game(rules=rules, player_index=PlayerIndex(0))

    assert player._rules is rules
    assert player._player_index == PlayerIndex(0)


def test_play_rejects_already_solved_position() -> None:
    player = HanoiPerfectPlayer()

    solved = HanoiPosition(n_pegs=3, disks=[2, 2], steps=3)

    try:
        player.play(solved)
        assert False, "play should raise ValueError for solved position"
    except ValueError as err:
        assert "already solved" in str(err)
