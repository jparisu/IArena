"""CLI entrypoint for IArena — play turn-based games in the terminal."""

from __future__ import annotations

import argparse

from iarena import __version__
from iarena.engine.Engine import Engine
from iarena.games.tictactoe.RandomTicTacToePlayer import RandomTicTacToePlayer
from iarena.games.tictactoe.TicTacToeASCIIView import TicTacToeASCIIView
from iarena.games.tictactoe.TicTacToeConfig import TicTacToeConfig
from iarena.games.tictactoe.TicTacToeRules import TicTacToeRules
from iarena.interface.TerminalInterface import TerminalInterface
from iarena.player.HumanPlayer import HumanPlayer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="iarena",
        description="IArena — play turn-based games in the terminal.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--game",
        choices=["tictactoe"],
        default="tictactoe",
        help="Game to play (default: tictactoe).",
    )
    parser.add_argument(
        "--players",
        type=int,
        choices=[1, 2],
        default=2,
        help="Number of human players (default: 2). Use 1 to play against a random bot.",
    )
    return parser


def _play_tictactoe(num_humans: int) -> int:
    config = TicTacToeConfig()
    rules = TicTacToeRules(config)
    view = TicTacToeASCIIView()
    interface = TerminalInterface(view)

    player1 = HumanPlayer(view, interface)
    player2: HumanPlayer | RandomTicTacToePlayer
    if num_humans == 2:
        player2 = HumanPlayer(view, interface)
    else:
        player2 = RandomTicTacToePlayer(rules)

    engine = Engine(rules, [player1, player2], interface)
    engine.run()
    return 0


def main() -> int:
    args = build_parser().parse_args()
    return _play_tictactoe(args.players)


if __name__ == "__main__":
    raise SystemExit(main())
