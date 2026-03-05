# Apps Overview

The `iarena.apping` module provides reusable components to build Streamlit apps
for IArena games, focused on one-player optimization flows.

## What It Provides

- Generic replay models (`OptimizationReplay`, `OptimizationReplayFrame`).
- A playback controller (`PlaybackController`) with:
  - play/pause,
  - step forward/backward,
  - slider seek support,
  - progress ratio.
- A game-page contract (`OptimizationGamePage`) so each game defines:
  - configuration widgets (left panel),
  - rules construction,
  - central position rendering,
  - optional secret-information rendering (collapsable panel),
  - default and extra player factories.
- Main-page index helpers:
  - `StreamlitGameIndex`
  - `render_games_index_page`

## Built-In Game Page

GoldMine includes `build_goldmine_streamlit_page()`, implemented on top of the
generic apping module. It demonstrates:

- left panel tabs (`Game`, `Players`, `Controls`),
- player selection including autonomous and playable modes,
- full-game replay generation,
- central panel for accumulated cost and movement options,
- optional hints,
- secret map information shown inside an expander.

## Play Modes

- Autonomous player selected:
  - The game runs fully.
  - The UI shows progression controls and each frame includes:
    - current position/state rendering,
    - movement taken to reach the next frame,
    - final score at terminal frame.
- Playable player selected (game-provided `play_from_ui`):
  - The app runs turn-by-turn.
  - The central panel shows current position and allowed movements.
  - After finishing, the app switches to replay/progression mode.

## Typical Usage

```python
import streamlit as st

from iarena.apping import build_default_game_index, render_games_index_page

render_games_index_page(
    streamlit_api=st,
    game_index=build_default_game_index(),
)
```

## Running The App

From the repository root:

```bash
streamlit run app/streamlit_app.py
```

`app/streamlit_app.py` automatically adds `<repo>/src` to `sys.path` before
importing `iarena`, so running as a script from the top folder works without
manually exporting `PYTHONPATH`.

## Streamlit Cloud

- App file: `app/streamlit_app.py`
- Working directory: repository root (default in Streamlit Cloud)

For dependencies, use a `requirements.txt` (or equivalent) that installs the
project with app extras, for example:

```text
-e .[app]
```
