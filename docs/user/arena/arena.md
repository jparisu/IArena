# Arena

An `Arena` executes a complete game session.

## Core Interface

`iarena.arening.Arena.Arena` defines:

- `play(rules, players, view) -> ScoreBoard`

`GenericArena` provides reusable loop structure and behavior hooks:

- turn execution,
- timeout checks,
- max-turn checks,
- score-limit checks,
- optional logging.

`DefaultArena` composes the default behavior set used by `ArenaFactory`.

## Factory

`iarena.arening.ArenaFactory.ArenaFactory` builds an arena from runtime constraints:

- `max_turns`
- `max_turn_time_s`
- `max_total_time_s`
- `score_limits`
- `store_logs`

## Typical Flow

1. A game generates `Rules` from a configuration.
2. Players and a view are selected.
3. An arena is created with `ArenaFactory`.
4. `arena.play(...)` returns a `ScoreBoard`.
