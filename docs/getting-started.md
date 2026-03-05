# Getting Started

Current repository status:

- package layout with `src/` structure,
- quality tooling (`ruff`, `mypy`, `pytest`, `codespell`),
- MkDocs documentation setup.

Next implementation milestones:

1. Define game interfaces and abstract base classes.
2. Add one reference game implementation.
3. Add one baseline player and tournament runner.
4. Expand tests for core game loop and player contracts.

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
