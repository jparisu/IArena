# Getting Started

Current repository status:

- package layout with `src/` structure,
- quality tooling (`ruff`, `mypy`, `pytest`, `codespell`),
- MkDocs documentation setup,
- one reference game (`GoldMine`) with rules, position, movement, generator,
  baseline player, and game orchestrator.

Next implementation milestones:

1. Define game interfaces and abstract base classes.
2. Expand the GoldMine reference game with additional player strategies.
3. Add one baseline player and tournament runner.
4. Expand tests for core game loop and player contracts.

## Generic players

The `iarena.playing` module provides reusable players that can be plugged into
any game rules implementation:

- `RandomPlayer`: samples uniformly from `rules.possible_movements(position)`.
  You can pass:
  - a `RandomGenerator` instance,
  - a `seed`,
  - or neither (it creates an unseeded generator, so runs differ over time).
- `TerminalPlayer`: lists legal movements in the terminal and asks the user to
  choose one by number. This is useful for debugging and non-graphical play.

## Optional capabilities

Games can optionally implement extra capabilities from
`iarena.utilizing.protocoling`, `iarena.interfacing.IPlayer`,
and `iarena.interfacing.IGameRules`:

- `ITextRenderable` for terminal output (`to_text`).
- `IPlotRenderable` for matplotlib/Streamlit-like plotting (`plot`).
- `IGameGenerator` to build rules from a dictionary (`build_game`).
- `ITerminalPlayer` for terminal-human play (`play_from_terminal`).
- `IGraphicalPlayer` for GUI-human play (`play_from_ui`).
- `IGameSolver` to expose min/max score bounds (`score_bounds`).

These are opt-in `Protocol`s, so games only implement what they need.

## Game orchestrator

Use `iarena.interfacing.IGameOrchestrator` to expose class references for one
game (rules, position, movement, player) and optional capabilities
(`terminal/gui player`, `solver`, `generator`, `text/plot`).

The orchestrator returns classes only, never instances, and provides `has_*`
helpers to detect optional interfaces.

## Arena loop

Use `iarena.interfacing.IArena` as an abstract base game loop object. It stores:

- one rules object,
- one current position,
- and one ordered collection of players.

Children implement `play() -> ScoreBoard`, and can reuse the default
`_play_loop()` helper to execute turns until `rules.finished(position)`.
