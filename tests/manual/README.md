# Manual Tests

This folder contains explicit manual runners that are **not** auto-executed by
`pytest`.

Run the GoldMine terminal runner directly:

```bash
python tests/manual/terminal_game_runner.py --help
```

Use an explicit map:

```bash
python tests/manual/terminal_game_runner.py \
  --map "1,1,3;2,4,2;1,1,1" \
  --start-row 0 --start-col 0 \
  --target-row 2 --target-col 2 \
  --hint-mode none
```

Or generate a uniform map from arguments and apply limits:

```bash
python tests/manual/terminal_game_runner.py \
  --rows 6 --cols 6 --default-cost 1.5 \
  --hint-mode compass \
  --per-turn-time-limit 20 \
  --game-time-limit 300 \
  --turn-limit 100 \
  --score-limit -20 \
  --store-information \
  --no-raise-on-stop
```
