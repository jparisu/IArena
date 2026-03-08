from __future__ import annotations

import pytest

from iarena.playing.PlayerIndex import PlayerIndex
from iarena.scoring.Score import Score
from iarena.scoring.ScoreBoard import ScoreBoard


def test_get_score_returns_score_for_requested_player_index() -> None:
    board = ScoreBoard()
    board._scores = {
        PlayerIndex(0): Score(10.0),
        PlayerIndex(1): Score(5.0),
    }

    score = board.get_score(PlayerIndex(0))

    assert score == Score(10.0)


def test_get_score_raises_key_error_for_unknown_player_index() -> None:
    board = ScoreBoard()
    board._scores = {PlayerIndex(0): Score(10.0)}

    with pytest.raises(KeyError):
        _ = board.get_score(PlayerIndex(9))
