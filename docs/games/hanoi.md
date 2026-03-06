# Hanoi

`Hanoi` is a single-player Towers of Hanoi game included as a simple IArena implementation.

## Rules Summary

- The puzzle contains `n_disks` disks and `n_pegs` pegs.
- All disks start stacked on `start_peg` in descending order (`n .. 1`).
- Each turn, exactly one top disk can move from one peg to another.
- A larger disk cannot be placed on top of a smaller disk.
- The game ends when all disks are stacked on `target_peg` in descending order.
- Score is the negative number of executed moves (fewer moves is better).

## Components

The Hanoi package provides:

- `HanoiGameRules` implementing `GameRules`.
- `HanoiPosition` implementing `Position` and `ITextRenderable`.
- `HanoiMovement` implementing `Movement` and `ITextRenderable`.
- `HanoiPlayer` as a deterministic baseline player.
- `HanoiGameConfiguration` as a typed configuration class (`from_dict`, `from_yaml`).
- `HanoiGameGenerator` implementing `GameGenerator`.
- `HanoiOrchestrator` implementing `GameOrchestrator`.

## Visual Layer

Visual rendering is intentionally not implemented yet for Hanoi.

- `terminal_game_class()` returns `None`.
- `streamlit_game_class()` returns `None`.
- `plot_renderable_class()` returns `None`.

This keeps the game focused on infrastructure validation through pure game logic.
