from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any

from iarena.interfacing.IGameRules import IGameGenerator, IGameRules, IGameSolver
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPlayer import IGraphicalPlayer, ITerminalPlayer
from iarena.interfacing.IPosition import IPosition
from iarena.interfacing.ScoreBoard import ScoreBoard
from iarena.utilizing.protocoling import (
    IPlotRenderable,
    ITextRenderable,
    as_text,
    supports_plotting,
    supports_text_rendering,
)


class DummyMovement(IMovement):
    pass


class DummyPosition(IPosition):
    def next_player(self) -> int:
        return 0


class DummyRules(IGameRules):
    def __init__(self, n_players: int) -> None:
        self._n_players = n_players

    def n_players(self) -> int:
        return self._n_players

    def first_position(self) -> IPosition:
        return DummyPosition()

    def next_position(self, movement: IMovement, position: IPosition) -> IPosition:
        return position

    def possible_movements(self, position: IPosition) -> Iterator[IMovement]:
        del position
        return iter([DummyMovement()])

    def finished(self, position: IPosition) -> bool:
        del position
        return False

    def score(self, position: IPosition) -> ScoreBoard:
        del position
        return ScoreBoard(self._n_players)


def test_text_rendering_is_optional_and_duck_typed() -> None:
    class TextPosition:
        def to_text(self) -> str:
            return "position in terminal"

    value = TextPosition()
    assert isinstance(value, ITextRenderable)
    assert supports_text_rendering(value)
    assert as_text(value) == "position in terminal"
    assert as_text(123) == "123"


def test_plot_rendering_is_optional_and_duck_typed() -> None:
    class PlotMovement:
        def plot(self, target: Any | None = None) -> dict[str, Any]:
            return {"target": target}

    movement = PlotMovement()
    assert isinstance(movement, IPlotRenderable)
    assert supports_plotting(movement)
    assert not supports_plotting("plain string")
    assert movement.plot("panel") == {"target": "panel"}


def test_game_generator_is_optional_and_accepts_dict_values() -> None:
    class DictGameGenerator:
        def build_game(self, values: Mapping[str, Any]) -> IGameRules:
            return DummyRules(n_players=int(values["n_players"]))

    generator = DictGameGenerator()
    assert isinstance(generator, IGameGenerator)
    rules = generator.build_game({"n_players": 2})
    assert rules.n_players() == 2


def test_terminal_and_graphical_player_capabilities_are_optional() -> None:
    class TerminalHuman:
        def play_from_terminal(self, position: IPosition) -> IMovement:
            del position
            return DummyMovement()

    class GraphicalHuman:
        def play_from_ui(self, position: IPosition, ui_context: Any | None = None) -> IMovement:
            del position, ui_context
            return DummyMovement()

    assert isinstance(TerminalHuman(), ITerminalPlayer)
    assert isinstance(GraphicalHuman(), IGraphicalPlayer)


def test_solver_returns_min_and_max_scoreboards() -> None:
    class BoundedSolver:
        def score_bounds(self, rules: IGameRules) -> tuple[ScoreBoard, ScoreBoard]:
            low = ScoreBoard(rules.n_players())
            high = ScoreBoard(rules.n_players())
            for player in range(rules.n_players()):
                low.define_score(player, -1.0)
                high.define_score(player, 1.0)
            return low, high

    solver = BoundedSolver()
    rules = DummyRules(n_players=3)
    assert isinstance(solver, IGameSolver)
    low, high = solver.score_bounds(rules)
    assert low.score == [-1.0, -1.0, -1.0]
    assert high.score == [1.0, 1.0, 1.0]
