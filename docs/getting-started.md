# Getting Started

## Install

Follow [Installation](installation.md).


## Play locally

### Launch the Terminal App

```bash
python -m apps.terminal_app.py
```

### Launch Streamlit App locally

```bash
streamlit run apps/streamlit_app.py
```

## Game design

The library is divided in several modules in order to make the implementation of games and players reusable and easy.

These are the main components of the library that a developer should know:

- `Rules` define game logic,
- `Position` define game state,
- `Movement` define state transitions,
- `Player` implementations decide actions,
- `Arena` implementations orchestrate game loop,
- `ScoreBoard` reports outcomes.


## Choose a Game and Run a Match

There is an specific *arena* that allows to play any game in a terminal interface.
In order to do so follow this instructions with the game desired:

``` python
    # TODO
```

## Add a new Game

!!! warning
    Coming soon.



## Tutorial

To get a more detailed tutorial, check the :ref:`tutorial` section.


## Explore APIs

- [Gaming API](api/gaming.md)
- [Playing API](api/playing.md)
- [Arening API](api/arening.md)
