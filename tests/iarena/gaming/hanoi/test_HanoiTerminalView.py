"""Tests for the Hanoi terminal view textual rendering behavior."""

from __future__ import annotations

from iarena.gaming.hanoi.HanoiConfiguration import HanoiConfiguration
from iarena.gaming.hanoi.HanoiRules import HanoiRules
from iarena.gaming.hanoi.HanoiTerminalView import HanoiTerminalView


def test_get_str_info_includes_instructions_and_goal() -> None:
    rules = HanoiRules(HanoiConfiguration(n_pegs=3, disks=[0, 0, 0]))
    view = HanoiTerminalView()

    text = view.get_str_info(rules)

    assert "Tower of Hanoi" in text
    assert "Goal peg" in text
    assert "Instructions" in text


def test_get_str_state_includes_board_and_possible_movements() -> None:
    rules = HanoiRules(HanoiConfiguration(n_pegs=3, disks=[0, 0, 0]))
    position = rules.first_position()
    view = HanoiTerminalView()

    text = view.get_str_state(position)

    assert "Towers:" in text
    assert "|" in text
    assert "3" in text
    assert "Possible movements:" in text
    assert "[0]" in text
