# GoldMine

`GoldMine` is a single-player grid exploration game included as a reference IArena implementation.

## Rules Summary

- The map stores positive digging costs.
- The player starts on one coordinate and that tile is already dug.
- Each turn, the player moves one step in a cardinal direction (`Up`, `Down`, `Left`, `Right`).
- Moving into a not-yet-dug tile adds that tile cost to the accumulated total.
- The game ends when the target coordinate (gold) has been dug.
- Final score is the negative accumulated cost (lower cost means better score).

## Components

The GoldMine package provides:

- `GoldMineGameRules` implementing `IGameRules`.
- `GoldMinePosition` implementing `IPosition`, `ITextRenderable`, and `IPlotRenderable`.
- `GoldMineMovement` implementing `IMovement` and `ITextRenderable`.
- `GoldMinePlayer` as a baseline greedy player.
- `GoldMineGameGenerator` implementing `IGameGenerator`.
- `GoldMineOrchestrator` implementing `IGameOrchestrator`.

`GoldMineGameRules` also implements `ITextRenderable`, so it can be used with
`TerminalArena` and manual terminal runners.

## Hints

GoldMine supports optional hint modes:

- `NONE`
- `COMPASS`
- `PROXIMITY`
- `DENSITY`

Only one mode is active per rules instance.
