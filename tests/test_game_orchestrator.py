from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any

from iarena.interfacing.IGameOrchestrator import IGameOrchestrator
from iarena.interfacing.IGameRules import IGameGenerator, IGameRules, IGameSolver
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPlayer import IGraphicalPlayer, IPlayer, ITerminalPlayer
from iarena.interfacing.IPosition import IPosition
from iarena.interfacing.ScoreBoard import ScoreBoard
from iarena.utilizing.protocoling import IPlotRenderable, ITextRenderable


class DummyMovement(IMovement):
    pass


class DummyPosition(IPosition):
    def next_player(self) -> int:
        return 0


class DummyRules(IGameRules):
    def n_players(self) -> int:
        return 2

    def first_position(self) -> IPosition:
        return DummyPosition()

    def next_position(self, movement: IMovement, position: IPosition) -> IPosition:
        del movement
        return position

    def possible_movements(self, position: IPosition) -> Iterator[IMovement]:
        del position
        return iter([DummyMovement()])

    def finished(self, position: IPosition) -> bool:
        del position
        return False

    def score(self, position: IPosition) -> ScoreBoard:
        del position
        return ScoreBoard(2)


class DummyPlayer(IPlayer):
    def play(self, position: IPosition) -> IMovement:
        del position
        return DummyMovement()


class DummyTerminalPlayer:
    def play_from_terminal(self, position: IPosition) -> IMovement:
        del position
        return DummyMovement()


class DummyGraphicalPlayer:
    def play_from_ui(self, position: IPosition, ui_context: Any | None = None) -> IMovement:
        del position, ui_context
        return DummyMovement()


class DummyGenerator:
    def build_game(self, values: Mapping[str, Any]) -> IGameRules:
        del values
        return DummyRules()


class DummySolver:
    def score_bounds(self, rules: IGameRules) -> tuple[ScoreBoard, ScoreBoard]:
        low = ScoreBoard(rules.n_players())
        high = ScoreBoard(rules.n_players())
        return low, high


class DummyTextRenderable:
    def to_text(self) -> str:
        return "text"


class DummyPlotRenderable:
    def plot(self, target: Any | None = None) -> Any:
        return target


def test_orchestrator_returns_classes_and_default_optional_capabilities_are_absent() -> None:
    class BasicOrchestrator(IGameOrchestrator):
        def game_rules_class(self) -> type[IGameRules]:
            return DummyRules

        def position_class(self) -> type[IPosition]:
            return DummyPosition

        def movement_class(self) -> type[IMovement]:
            return DummyMovement

        def player_class(self) -> type[IPlayer]:
            return DummyPlayer

    orchestrator = BasicOrchestrator()
    assert orchestrator.game_rules_class() is DummyRules
    assert orchestrator.position_class() is DummyPosition
    assert orchestrator.movement_class() is DummyMovement
    assert orchestrator.player_class() is DummyPlayer
    assert not orchestrator.has_terminal_player()
    assert not orchestrator.has_graphical_player()
    assert not orchestrator.has_game_generator()
    assert not orchestrator.has_game_solver()
    assert not orchestrator.has_text_rendering()
    assert not orchestrator.has_plotting()


def test_orchestrator_exposes_optional_capability_classes_and_flags() -> None:
    class FullOrchestrator(IGameOrchestrator):
        def game_rules_class(self) -> type[IGameRules]:
            return DummyRules

        def position_class(self) -> type[IPosition]:
            return DummyPosition

        def movement_class(self) -> type[IMovement]:
            return DummyMovement

        def player_class(self) -> type[IPlayer]:
            return DummyPlayer

        def terminal_player_class(self) -> type[ITerminalPlayer] | None:
            return DummyTerminalPlayer

        def graphical_player_class(self) -> type[IGraphicalPlayer] | None:
            return DummyGraphicalPlayer

        def game_generator_class(self) -> type[IGameGenerator] | None:
            return DummyGenerator

        def game_solver_class(self) -> type[IGameSolver] | None:
            return DummySolver

        def text_renderable_class(self) -> type[ITextRenderable] | None:
            return DummyTextRenderable

        def plot_renderable_class(self) -> type[IPlotRenderable] | None:
            return DummyPlotRenderable

    orchestrator = FullOrchestrator()
    assert orchestrator.terminal_player_class() is DummyTerminalPlayer
    assert orchestrator.graphical_player_class() is DummyGraphicalPlayer
    assert orchestrator.game_generator_class() is DummyGenerator
    assert orchestrator.game_solver_class() is DummySolver
    assert orchestrator.text_renderable_class() is DummyTextRenderable
    assert orchestrator.plot_renderable_class() is DummyPlotRenderable
    assert orchestrator.has_terminal_player()
    assert orchestrator.has_graphical_player()
    assert orchestrator.has_game_generator()
    assert orchestrator.has_game_solver()
    assert orchestrator.has_text_rendering()
    assert orchestrator.has_plotting()
