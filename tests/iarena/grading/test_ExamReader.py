from __future__ import annotations

from pathlib import Path

import pytest

from iarena.gaming.Movement import Movement
from iarena.gaming.Position import Position
from iarena.gaming.Rules import Rules
from iarena.grading.ExamReader import ExamReader
from iarena.playing.Player import Player
from iarena.playing.PlayerIndex import PlayerIndex


class _Player(Player):
    def name(self) -> str:
        return "reader-player"

    def play(self, pos: Position) -> Movement:
        return next(pos.get_rules().possible_movements(pos))

    def starting_game(self, rules: Rules, player_index: PlayerIndex) -> None:
        _ = rules
        _ = player_index


def test_from_mapping_builds_exam_with_expanded_trials_and_limits() -> None:
    exam = ExamReader.from_mapping(
        configuration={
            "game": "hanoi",
            "move_timeout_s": 0.2,
            "total_timeout_s": 1.0,
            "repetitions": 2,
            "max_moves": 10,
            "trials": [
                {
                    "name": "suite-trial",
                    "value": 2.5,
                    "args": {"n_pegs": 3},
                    "multi_args": {"n_disks": [1, 2]},
                },
            ],
        },
        player=_Player(),
    )

    assert exam.game.name() == "hanoi"
    assert len(exam.trial_configurations) == 2
    assert all(configuration.repetitions == 2 for configuration in exam.trial_configurations)
    assert all(configuration.value == 2.5 for configuration in exam.trial_configurations)
    assert all(configuration.min_score <= configuration.max_score for configuration in exam.trial_configurations)
    assert all(configuration.min_score == configuration.max_score for configuration in exam.trial_configurations)


def test_from_file_reads_trials_configuration(tmp_path: Path) -> None:
    configuration_file = tmp_path / "exam_reader.yaml"
    configuration_file.write_text(
        "\n".join(
            [
                "game: hanoi",
                "repetitions: 3",
                "trials:",
                "  - args:",
                "      n_pegs: 3",
                "      n_disks: 1",
            ],
        ),
        encoding="utf-8",
    )

    exam = ExamReader.from_file(configuration_file=str(configuration_file), player=_Player())

    assert len(exam.trial_configurations) == 1
    assert exam.trial_configurations[0].repetitions == 3
    assert exam.trial_configurations[0].value == 1.0


def test_from_mapping_raises_when_game_has_no_oracle() -> None:
    with pytest.raises(RuntimeError, match="does not expose any oracle class"):
        _ = ExamReader.from_mapping(
            configuration={
                "game": "tictactoe",
                "trials": [{"args": {"board_size": 3, "win_length": 3}}],
            },
            player=_Player(),
        )
