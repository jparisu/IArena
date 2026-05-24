# Games Overview

This section documents the game abstraction model used in IArena.

## Core Interfaces

### Configuration

`Configuration` defines parameters to create a `Rules` instance.
It is usually a `dataclass` that holds information to create a rule set for a specific game.
Different games would have different configuration parameters.


### Rules

`Rules` represents the rules engine of a game. It defines:

* number of players
* starting position
* state transitions
* legal moves
* termination condition
* scoring

#### Methods

| Method                                                    | Type     | Description                    |
| --------------------------------------------------------- | -------- | ------------------------------ |
| `n_players() -> int`                                      | function | Returns number of players      |
| `first_position() -> Position`                            | function | Returns the initial position   |
| `next_position(pos: Position, mov: Movement) -> Position` | function | Computes the next state        |
| `possible_movements(pos: Position) -> Iterator[Movement]` | function | Generates legal moves          |
| `is_finished(pos: Position) -> bool`                      | function | Checks if the game is finished |
| `get_score(pos: Position) -> ScoreBoard`                  | function | Returns score for the position |

### Position

Represents a game state.

#### Methods

| Method                         | Type     | Description               |
| ------------------------------ | -------- | ------------------------- |
| `next_player() -> PlayerIndex` | function | Player that should act    |
| `get_rules() -> Rules`         | function | Associated rules instance |

### Movement

Represents an action that transitions between states.


## ScoreBoard

Stores one score per player.

Example method:

```
get_score(index) -> float
```

## Built-in Games

* hanoi
* tictactoe
* goldmine

## Game Characteristics

| Game      | Players | Deterministic | Perfect Information | Zero-Sum   |
| --------- | ------- | ------------- | ------------------- | ---------- |
| Hanoi     | 1       | Yes           | Yes                 | No         |
| TicTacToe | 2       | Yes           | Yes                 | Yes        |
| Goldmine  | 1       | No            | No                  | No         |
