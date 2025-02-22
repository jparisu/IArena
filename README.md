# IArena

<img src="resources/images/logo.webp" alt="drawing" width="20%"/>

[![Documentation Status](https://readthedocs.org/projects/iarena/badge/?version=latest)](https://iarena.readthedocs.io/en/latest/)

**Framework** for testing **AI** system in basic or logic games.

## Documentation

The documentation is available at [Read the Docs](https://iarena.readthedocs.io/en/latest/).


## Architecture

### Interfaces

This repository define some interfaces under `src/IArena/interfaces` that define these basic concepts:

- `IMovement`: define a movement from a position to another.
- `IPosition`: define a specific position or board in the game.
- `IPlayer`: define a player that is able to play a movement from a position given.
- `IGameRules`: define the rules of the game and implement the logic of the game by given the movements possible and the next positions from a position and movement given.

### Games

There are some games implemented under `src/IArena/games`:

- `Hanoi`: Towers of Hanoi.
- `BlindWalk`: Weighted grid to find the lowest cost path.
- `FieldWalk`: Similar to `BlindWalk` but with access to the whole map from the beginning.
- `Coins`: 2 player Roman coins game.
- `Nim`: 2 player well known Nim game.
- ...

### Players

There are some players implemented under `src/IArena/players`:

- `PlayablePlayer`: Ask the user for the movement to play by keyboard.
- `RandomPlayer`: Play a random movement from the movements possible.
- `FirstPlayer`: Play the first movement from the movements possible.
- `LastPlayer`: Play the last movement from the movements possible.
- ...

### Arena

Implementations of different ways of playing and measuring scores:

- `GenericGame`: Decide the rules and the players and create a basic loop game.
- `BroadcastGame`: Similar to `GenericGame` but print out the player actions.
- `PlayableGame`: Play a game with all players `PlayablePlayer`.
- ...

---

## Resources

There are some resources under `resources` folder with util information and implementations:

- `play_hanoi.ipynb`: Jupyter notebook to play Towers of Hanoi. It installs and plays all along.
- `create_player_coins.ipynb`: Jupyter notebook with everything set up to create a player and play against a random player `Coins` game.

---

## Installation

### From source

```bash
pip install --upgrade git+https://github.com/jparisu/IArena.git
```
