# Arenas

The `iarena.arening` module implements concrete arena loops and composable
arena behaviors.

## GenericArena

`GenericArena` is the default loop implementation for any `GameRules` game.
It iterates turns by asking the active player (`position.next_player()`) for a
movement via `play(position)`, validates legality, applies the movement, and
returns a final `ScoreBoard`.

When a stop condition triggers, `GenericArena` raises `ArenaStoppedError` by
default with the stop reason and final/failure score. Set `raise_on_stop=False`
to return the score instead of raising.

## Composable behaviors

Use `ArenaFactory` or pass behaviors directly into `GenericArena`:

- `PerTurnTimeLimitCondition`: player loses when one turn exceeds time limit.
- `GameTimeLimitCondition`: all players receive bad result when game exceeds
  total time limit.
- `TurnLimitCondition`: all players receive bad result when game exceeds turn
  limit.
- `ScoreLimitCondition`: game stops when any player reaches a minimum score.
- `GameHistoryObserver`: stores positions and movements for replay/analysis.

Per-turn timeout behavior executes `play` in a worker thread and interrupts it
on timeout (best-effort), while propagating worker exceptions to the main
arena thread.

## TerminalArena

`TerminalArena` extends `GenericArena` with terminal rendering. It prints game
rules at start, prints position each turn, and logs selected movements.

`TerminalArena` requires rules to implement `TerminalGame` from
`iarena.desining.visualing`. That interface requires:

- `position_to_terminal(position)` (required),
- optional `terminal_instructions()`,
- optional `movement_from_terminal(raw_movement, possible_movements)`,
- optional `movement_to_terminal(movement)`.

## Factory usage

```python
from iarena.arening import ArenaFactory

arena = ArenaFactory.build(
    rules=rules,
    players=players,
    per_turn_time_limit_seconds=2.0,
    game_time_limit_seconds=60.0,
    turn_limit=200,
    score_limit=100.0,
    store_information=True,
    terminal=False,
    raise_on_stop=False,
)

final_score = arena.play()
record = arena.game_record()  # available if store_information=True
```
