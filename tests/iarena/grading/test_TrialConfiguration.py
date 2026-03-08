from __future__ import annotations

from typing import Iterator

from iarena.gaming.Rules import Rules
from iarena.gaming.Movement import Movement
from iarena.gaming.Position import Position
from iarena.grading.MatchConfiguration import MatchConfiguration
from iarena.grading.TrialConfiguration import TrialConfiguration
from iarena.playing.Player import Player
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.scoring.ScoreBoard import ScoreBoard
from iarena.scoring.Score import Score


class _Rules(Rules):
    def n_players(self) -> int:
        return 2

    def first_position(self) -> Position:
        raise NotImplementedError

    def next_position(self, pos: Position, mov: Movement) -> Position:
        raise NotImplementedError

    def possible_movements(self, pos: Position) -> Iterator[Movement]:
        return iter(())

    def is_finished(self, pos: Position) -> bool:
        return False

    def get_score(self, pos: Position) -> ScoreBoard:
        raise NotImplementedError


class _Player(Player):
    def name(self) -> str:
        return "player"

    def play(self, pos: Position) -> Movement:
        _ = pos
        raise NotImplementedError

    def starting_game(self, rules: Rules, player_index: PlayerIndex) -> None:
        _ = rules
        _ = player_index


def test_trial_configuration_stores_expected_trial_inputs() -> None:
    match_configuration = MatchConfiguration(
        move_timeout_s=1.0,
        total_timeout_s=10.0,
        max_turns=50,
        score_limits=(Score(-1.0), Score(1.0)),
    )
    players = [_Player(), _Player()]

    configuration = TrialConfiguration(
        match_configuration=match_configuration,
        trialing_player_index=PlayerIndex(0),
        rules=_Rules(),
        players=players,
        repetitions=3,
        allow_fails=1,
    )

    assert configuration.match_configuration is match_configuration
    assert configuration.trialing_player_index == PlayerIndex(0)
    assert isinstance(configuration.rules, _Rules)
    assert configuration.players == players
    assert configuration.repetitions == 3
    assert configuration.allow_fails == 1
