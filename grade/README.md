# Single-File Grader Script

`grade/grader_script.py` grades one player `.py` or `.ipynb` file with one YAML grading configuration.

## Usage

From repository root:

```bash
python grade/grader_script.py \
  --configuration-file resources/graders/IA_ECOMAT_2526_goldmine_empty.yaml \
  --player-file resources/players/player_template.py
```

Optional arguments:

- `--debug`: run grading with `DebugLevel.DEBUG`.
- `--output-file <path>`: write the JSON result to a file.
- `--token <str>`: token used to select the notebook code cell to execute when `--player-file` is `.ipynb` (default: `"PLAYER ="`).

Example with output file:

```bash
python grade/grader_script.py \
  --configuration-file resources/graders/IA_ECOMAT_2526_goldmine_empty.yaml \
  --player-file resources/players/player_template.py \
  --output-file /tmp/grading_result.json
```

## Output

The script prints a JSON summary to stdout, for example:

```json
{
  "configuration_file": "resources/graders/IA_ECOMAT_2526_goldmine_empty.yaml",
  "debug_level": "USER",
  "n_error_matches": 0,
  "n_matches": 30,
  "n_trials": 10,
  "n_warning_matches": 2,
  "player_file": "resources/players/player_template.py",
  "token": "PLAYER =",
  "score": 42.5
}
```

Fields:

- `score`: final exam score for the player.
- `n_trials`: number of expanded trials executed.
- `n_matches`: total number of played matches (including repetitions).
- `n_warning_matches`: matches with warning messages (for example, score outside allowed trial limits).
- `n_error_matches`: matches that ended with execution errors.
