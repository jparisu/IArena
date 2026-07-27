"""Streamlit entrypoint for IArena — play turn-based games in the browser."""

from __future__ import annotations

from dataclasses import dataclass, field

import streamlit as st

from iarena.game.GameRules import GameRules
from iarena.game.GameState import GameState
from iarena.interface.StreamlitInterface import StreamlitInterface
from iarena.player.Player import Player
from iarena.view.StreamlitView import StreamlitView

# ---------------------------------------------------------------------------
# Generic game session dataclass
# ---------------------------------------------------------------------------


@dataclass
class StreamlitGame:
    """All components needed to run one game session in the browser.

    Parameters
    ----------
    rules:
        Game rules (legal moves, state transitions, terminal test, result).
    view:
        Streamlit-capable view that renders state and exposes
        ``pop_pending_move``.
    bots:
        Mapping of player index to an automatic player.  Indices absent
        from this dict are treated as human turns.
    player_names:
        Display names for each player index (e.g. ``{0: "X", 1: "O"}``).
    """

    rules: GameRules
    view: StreamlitView
    bots: dict[int, Player] = field(default_factory=dict)
    player_names: dict[int, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# TicTacToe game builder
# ---------------------------------------------------------------------------


def _build_tictactoe(num_humans: int) -> StreamlitGame:
    from iarena.games.tictactoe.RandomTicTacToePlayer import RandomTicTacToePlayer
    from iarena.games.tictactoe.TicTacToeConfig import TicTacToeConfig
    from iarena.games.tictactoe.TicTacToeRules import TicTacToeRules
    from iarena.games.tictactoe.TicTacToeStreamlitView import TicTacToeStreamlitView

    config = TicTacToeConfig()
    rules = TicTacToeRules(config)
    view = TicTacToeStreamlitView()
    bots: dict[int, Player] = {}
    if num_humans < 2:
        bots[1] = RandomTicTacToePlayer(rules)
    return StreamlitGame(
        rules=rules,
        view=view,
        bots=bots,
        player_names={0: "X", 1: "O"},
    )


# Registry: game name -> builder(num_humans) -> StreamlitGame
_GAME_BUILDERS: dict[str, object] = {
    "tictactoe": _build_tictactoe,
}

# ---------------------------------------------------------------------------
# Generic game runner
# ---------------------------------------------------------------------------

_STATE_KEYS = ("game_state", "game_over", "game_result")


def _init_session(rules: GameRules) -> None:
    st.session_state.game_state = rules.first_position()
    st.session_state.game_over = False
    st.session_state.game_result = None


def _reset_session() -> None:
    for key in _STATE_KEYS:
        st.session_state.pop(key, None)


def _run_game(game: StreamlitGame) -> None:
    """Drive one step of the game loop and render the current state.

    Called on every Streamlit rerun.  Applies a bot move immediately
    (triggering another rerun) or waits for a human to click a cell.
    """
    rules = game.rules
    interface = StreamlitInterface(game.view)

    if "game_state" not in st.session_state:
        _init_session(rules)

    state: GameState = st.session_state.game_state

    # ---- terminal: show result and final board ---------------------------
    if st.session_state.game_over:
        result = st.session_state.game_result
        if result is None:
            st.success("It's a draw!")
        else:
            winner = game.player_names.get(result, str(result))
            st.success(f"Player {winner} wins!")
        game.view.render_state(state, interface)
        return

    current = state.current_player_id()
    player_name = game.player_names.get(current, str(current))

    # ---- bot turn: apply move and rerun ---------------------------------
    if current in game.bots:
        bot = game.bots[current]
        move = bot.choose_move(state)
        state = rules.apply_move(state, move)
        st.session_state.game_state = state
        if rules.is_terminal(state):
            st.session_state.game_over = True
            st.session_state.game_result = rules.result(state)
        st.rerun()
        return

    # ---- human turn: render board and handle pending click --------------
    st.info(f"Player **{player_name}**'s turn — click a cell to play.")
    game.view.render_state(state, interface)

    move = game.view.pop_pending_move()
    if move is not None and rules.is_legal(state, move):
        state = rules.apply_move(state, move)
        st.session_state.game_state = state
        if rules.is_terminal(state):
            st.session_state.game_over = True
            st.session_state.game_result = rules.result(state)
        st.rerun()


# ---------------------------------------------------------------------------
# App entry point
# ---------------------------------------------------------------------------


def main() -> None:
    st.set_page_config(page_title="IArena", page_icon="♟", layout="centered")
    st.title("IArena")

    with st.sidebar:
        st.header("Settings")
        game_name: str = st.selectbox(
            "Game",
            list(_GAME_BUILDERS.keys()),
            format_func=str.title,
        )
        num_humans: int = st.radio(
            "Human players",
            [1, 2],
            format_func=lambda n: f"{n}" + (" (vs bot)" if n == 1 else ""),
            horizontal=True,
        )
        if st.button("New Game", type="primary", use_container_width=True):
            _reset_session()
            st.rerun()

    builder = _GAME_BUILDERS[game_name]
    game = builder(num_humans)
    _run_game(game)


if __name__ == "__main__":
    main()
