"""Manual terminal runner focused on the GoldMine game.

This module is intentionally placed under ``tests/manual`` and is not named
``test_*.py``, so it is not auto-collected by pytest. Run it explicitly with:

    python tests/manual/terminal_game_runner.py --help
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from iarena.arening import ArenaFactory, ArenaStoppedError, GenericArena
from iarena.gaming.GoldMine import GoldMineGameGenerator
from iarena.desining.gaming.GameRules import GameRules
from iarena.desining.playing.Player import Player
from iarena.playing.TerminalPlayer import TerminalPlayer


def _parse_map(raw_map: str) -> list[list[float]]:
    """Parse a compact matrix string into a GoldMine cost map.

    Format: ``row1;row2;...`` where each row is comma-separated values.
    Example: ``"1,2,3;4,5,6"``.

    Args:
        raw_map: Raw map string.

    Returns:
        Parsed 2D cost matrix.

    Raises:
        ValueError: If the map has invalid shape or values.
    """
    rows = [row.strip() for row in raw_map.split(";") if row.strip()]
    if not rows:
        raise ValueError("--map cannot be empty")

    parsed_rows: list[list[float]] = []
    expected_columns: int | None = None
    for row in rows:
        values = [value.strip() for value in row.split(",") if value.strip()]
        if not values:
            raise ValueError("each map row must contain at least one numeric value")
        parsed_row = [float(value) for value in values]
        if any(value <= 0.0 for value in parsed_row):
            raise ValueError("all map values must be > 0")
        if expected_columns is None:
            expected_columns = len(parsed_row)
        elif len(parsed_row) != expected_columns:
            raise ValueError("all map rows must have the same number of columns")
        parsed_rows.append(parsed_row)
    return parsed_rows


def _build_default_map(rows: int, cols: int, default_cost: float) -> list[list[float]]:
    """Build a rectangular GoldMine cost map with uniform values.

    Args:
        rows: Number of rows.
        cols: Number of columns.
        default_cost: Default digging cost for all cells.

    Returns:
        Uniform cost matrix.

    Raises:
        ValueError: If rows/cols/default_cost are invalid.
    """
    if rows <= 0:
        raise ValueError("--rows must be > 0")
    if cols <= 0:
        raise ValueError("--cols must be > 0")
    if default_cost <= 0.0:
        raise ValueError("--default-cost must be > 0")
    return [[default_cost for _ in range(cols)] for _ in range(rows)]


def _build_rules_and_players(arguments: argparse.Namespace) -> tuple[GameRules, list[Player]]:
    """Build GoldMine rules and terminal player from CLI arguments.

    Args:
        arguments: Parsed command-line arguments.

    Returns:
        Tuple with game rules and players.

    Raises:
        ValueError: If coordinates are out of map bounds.
    """
    cost_map = _parse_map(arguments.map) if arguments.map is not None else _build_default_map(
        rows=arguments.rows,
        cols=arguments.cols,
        default_cost=arguments.default_cost,
    )

    n_rows = len(cost_map)
    n_cols = len(cost_map[0])

    # Backward-compatible aliases:
    # - x is interpreted as column.
    # - y is interpreted as row.
    start_row = arguments.start_row if arguments.start_row is not None else arguments.start_y
    start_col = arguments.start_col if arguments.start_col is not None else arguments.start_x
    target_row = arguments.target_row if arguments.target_row is not None else arguments.target_y
    target_col = arguments.target_col if arguments.target_col is not None else arguments.target_x

    if target_row is None:
        target_row = n_rows - 1
    if target_col is None:
        target_col = n_cols - 1

    # GoldMine/SquareMap coordinate convention is (x=row, y=col).
    start = (start_row, start_col)
    target = (target_row, target_col)

    for coordinate_name, coordinate in (("start", start), ("target", target)):
        x_value, y_value = coordinate
        if x_value < 0 or x_value >= n_rows or y_value < 0 or y_value >= n_cols:
            raise ValueError(
                f"{coordinate_name} coordinate ({x_value}, {y_value}) is outside map bounds "
                f"rows[0..{n_rows - 1}] cols[0..{n_cols - 1}]"
            )

    rules = GoldMineGameGenerator().build_game(
        {
            "map": cost_map,
            "start": start,
            "target": target,
            "hint_mode": arguments.hint_mode,
        }
    )
    return rules, [TerminalPlayer()]


def build_parser() -> argparse.ArgumentParser:
    """Build command-line parser for manual GoldMine runner.

    Args:
        None.

    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(description="Manual terminal runner for GoldMine.")
    parser.add_argument(
        "--map",
        type=str,
        default=None,
        help=(
            "Optional explicit map string: '1,2,3;4,5,6'. "
            "If omitted, a uniform map is generated from --rows/--cols/--default-cost."
        ),
    )
    parser.add_argument("--rows", type=int, default=4, help="Rows used when --map is omitted.")
    parser.add_argument("--cols", type=int, default=5, help="Columns used when --map is omitted.")
    parser.add_argument(
        "--default-cost",
        type=float,
        default=1.0,
        help="Cell cost used by generated uniform map when --map is omitted.",
    )
    parser.add_argument("--start-row", type=int, default=None, help="Start row index.")
    parser.add_argument("--start-col", type=int, default=None, help="Start column index.")
    parser.add_argument(
        "--start-x",
        type=int,
        default=0,
        help="Deprecated alias for --start-col (kept for backward compatibility).",
    )
    parser.add_argument(
        "--start-y",
        type=int,
        default=0,
        help="Deprecated alias for --start-row (kept for backward compatibility).",
    )
    parser.add_argument(
        "--target-row",
        type=int,
        default=None,
        help="Target row index; defaults to bottom map row.",
    )
    parser.add_argument(
        "--target-col",
        type=int,
        default=None,
        help="Target column index; defaults to rightmost map column.",
    )
    parser.add_argument(
        "--target-x",
        type=int,
        default=None,
        help="Deprecated alias for --target-col (kept for backward compatibility).",
    )
    parser.add_argument(
        "--target-y",
        type=int,
        default=None,
        help="Deprecated alias for --target-row (kept for backward compatibility).",
    )
    parser.add_argument(
        "--hint-mode",
        choices=["none", "compass", "proximity", "density"],
        default="none",
        help="GoldMine hint mode.",
    )
    parser.add_argument(
        "--per-turn-time-limit",
        type=float,
        default=None,
        help="Maximum seconds per turn; offender receives penalty score.",
    )
    parser.add_argument(
        "--game-time-limit",
        type=float,
        default=None,
        help="Maximum seconds for whole game; all players receive penalty.",
    )
    parser.add_argument(
        "--turn-limit",
        type=int,
        default=None,
        help="Maximum number of turns before all players receive penalty.",
    )
    parser.add_argument(
        "--score-limit",
        type=float,
        default=None,
        help="Stop game when any player reaches or exceeds this score.",
    )
    parser.add_argument(
        "--store-information",
        action="store_true",
        help="Store movements/positions and print summary at the end.",
    )
    parser.add_argument(
        "--penalty-score",
        type=float,
        default=-math.inf,
        help="Penalty value used for timeout/turn-limit results.",
    )
    parser.add_argument(
        "--no-raise-on-stop",
        action="store_true",
        help="Return failure score on stop conditions instead of raising exceptions.",
    )
    return parser


def run_manual_game(arguments: argparse.Namespace) -> int:
    """Run a manual GoldMine game in terminal with optional limits.

    Args:
        arguments: Parsed command-line arguments.

    Returns:
        Exit code: ``0`` on success, ``1`` on invalid setup.
    """
    try:
        rules, players = _build_rules_and_players(arguments)
    except ValueError as error:
        print(f"Invalid game setup: {error}")
        return 1

    arena = ArenaFactory.build(
        rules=rules,
        players=players,
        terminal=True,
        per_turn_time_limit_seconds=arguments.per_turn_time_limit,
        game_time_limit_seconds=arguments.game_time_limit,
        turn_limit=arguments.turn_limit,
        score_limit=arguments.score_limit,
        store_information=arguments.store_information,
        penalty_score=arguments.penalty_score,
        raise_on_stop=not arguments.no_raise_on_stop,
    )

    if not isinstance(arena, GenericArena):
        raise RuntimeError("ArenaFactory.build() returned an unexpected arena type")

    try:
        final_score = arena.play()
    except ArenaStoppedError as error:
        print(f"Game stopped: {error.reason}")
        print("Failure score board:", error.final_score)
        return 0

    print("Final score board:", final_score)
    game_record = arena.game_record()
    if arguments.store_information and game_record is not None:
        print(f"Stored turns: {len(game_record.turn_records)}")
        print(f"End reason: {game_record.end_reason}")
    return 0


def main() -> int:
    """CLI entrypoint for manual terminal GoldMine runner.

    Args:
        None.

    Returns:
        Process exit code.
    """
    parser = build_parser()
    arguments = parser.parse_args()
    return run_manual_game(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
