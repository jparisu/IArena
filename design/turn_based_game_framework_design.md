# Turn-Based Game Framework Design

## 1. Objective

The goal is to design a sufficiently abstract framework for implementing turn-based games.

The framework should support games regardless of:

- Number of players.
- Type of information available to each player.
- Whether the game is zero-sum or not.
- Specific game mechanics.

The only core restriction is:

> The game must be turn-based.

The architecture is divided into several modules:

1. `game`
2. `engine`
3. `interface`
4. `view`
5. `player`

---

## 2. Module: `game`

This module contains the abstract foundations required to define any concrete game.

It should not contain a specific game implementation. Instead, it defines the generic contracts that concrete games must implement.

### Main responsibility

Represent the structure of a turn-based game independently of its concrete rules, players, or interface.

### Abstract classes

#### `GameConfig`

Represents the static configuration of a game.

##### Responsibilities

- Store the parameters needed to initialize a specific game.
- Define game-level constants or options.
- Support different numbers of players.
- Support different game modes or variants.
- Provide the initial setup required by the rules and state.

##### Examples of information it may contain

- Number of players.
- Board size.
- Initial resources.
- Variant-specific parameters.
- Whether hidden information exists.
- Maximum number of turns, if applicable.

##### Notes

This class should remain abstract and game-independent. Each concrete game defines its own configuration class.

---

#### `GameRules`

Defines the logic and rules of a concrete game.

##### Responsibilities

- Determine which moves are legal in a given state.
- Apply a move to a state and produce the next state.
- Determine whether the game has ended.
- Determine the current player or next player, when this is rule-dependent.
- Validate moves.
- Calculate outcomes, scores, rewards, or winners.

##### Typical methods

```python
class GameRules:
    def legal_moves(self, state: "GameState") -> list["Move"]:
        ...

    def apply_move(self, state: "GameState", move: "Move") -> "GameState":
        ...

    def is_terminal(self, state: "GameState") -> bool:
        ...

    def result(self, state: "GameState"):
        ...
```

##### Notes

The rules should not depend on a concrete user interface. They should be pure game logic.

---

#### `GameState`

Represents the current position or state of the game.

##### Responsibilities

- Store all dynamic information needed to describe the current game position.
- Represent whose turn it is.
- Represent public and possibly private information.
- Support games with arbitrary numbers of players.
- Provide enough information for rules, players, and views to operate.

##### Examples of information it may contain

- Current turn number.
- Active player.
- Board position.
- Hands, cards, pieces, resources, or hidden information.
- Game history, if needed.
- Scores or accumulated rewards.

##### Notes

The state should be generic enough to support games with complete or incomplete information.

Depending on the implementation strategy, the state may be immutable, copied after each move, or mutated in place by the rules.

---

#### `Move`

Represents an action that a player can perform from a given game state.

##### Responsibilities

- Encode a player's decision.
- Contain enough information for the rules to validate and apply the move.
- Be independent of how the move was selected.
- Support both human and automatic players.

##### Examples

- Moving a piece.
- Playing a card.
- Choosing an action.
- Passing a turn.
- Selecting an option from a list of legal actions.

##### Notes

A move should not contain interface-specific information. The same move object should be usable whether it came from a terminal, Streamlit app, HTML interface, or automatic player.

---

## 3. Module: `engine`

The engine is the object that runs a game loop over a game.

It coordinates the rules, state, players, and interface.

### Main responsibility

Execute the turn-based game loop.

### Class: `Engine`

Represents a game runner.

#### Attributes

```python
class Engine:
    rules: GameRules
    state: GameState
    players: list["Player"]
    interface: "Interface"
```

#### Responsibilities

- Hold the current game state.
- Hold the game rules or game logic.
- Hold the list of players.
- Hold the interface used to communicate game information.
- Iterate over turns.
- Ask the active player to choose a move for the current position.
- Validate or delegate validation of the selected move.
- Apply the move using the game rules.
- Update the current state.
- Notify the interface and/or view about relevant changes.
- Stop when the game reaches a terminal state.

#### Basic loop

```python
class Engine:
    def run(self):
        while not self.rules.is_terminal(self.state):
            current_player = self.get_current_player()
            move = current_player.choose_move(self.state)
            self.state = self.rules.apply_move(self.state, move)

        return self.rules.result(self.state)
```

#### More complete loop

```python
class Engine:
    def run(self):
        self.interface.on_game_start(self.state)

        while not self.rules.is_terminal(self.state):
            current_player = self.get_current_player()

            self.interface.on_turn_start(self.state, current_player)

            move = current_player.choose_move(self.state)

            if move not in self.rules.legal_moves(self.state):
                self.interface.on_invalid_move(self.state, current_player, move)
                continue

            self.state = self.rules.apply_move(self.state, move)

            self.interface.on_turn_end(self.state, current_player, move)

        result = self.rules.result(self.state)
        self.interface.on_game_end(self.state, result)

        return result
```

#### Notes

The engine should not contain game-specific logic. It should only coordinate the flow of the game.

Different engines may exist if different game-loop strategies are needed.

Examples:

- Standard sequential turn engine.
- Engine with logging.
- Engine for simulations.
- Engine for human-interactive play.
- Engine for AI-vs-AI evaluation.

---

## 4. Module: `interface`

The interface module defines how the system communicates information externally.

Interfaces are responsible for the interaction medium, not for game rules.

### Main responsibility

Provide a common communication layer between the engine, the view, and the outside environment.

### Abstract class: `Interface`

Base interface contract for all concrete interfaces.

#### Responsibilities

- Display information to the user or environment.
- Receive user input when needed.
- Notify about game events.
- Provide a common protocol for all interface implementations.

#### Possible methods

```python
class Interface:
    def render(self, content: str) -> None:
        ...

    def ask(self, prompt: str) -> str:
        ...

    def on_game_start(self, state: GameState) -> None:
        ...

    def on_turn_start(self, state: GameState, player: "Player") -> None:
        ...

    def on_invalid_move(self, state: GameState, player: "Player", move: Move) -> None:
        ...

    def on_turn_end(self, state: GameState, player: "Player", move: Move) -> None:
        ...

    def on_game_end(self, state: GameState, result) -> None:
        ...
```

---

### Concrete interface: `NullInterface`

An empty interface for games or simulations that do not need any user-facing interface.

#### Responsibilities

- Do nothing when rendering information.
- Return no interaction unless explicitly required.
- Support automatic players and simulations.
- Allow the engine to run without visual output.

#### Use cases

- AI-vs-AI games.
- Batch simulations.
- Automated tests.
- Reinforcement learning experiments.
- Backend-only execution.

---

### Concrete interface: `TerminalInterface`

A text-based interface using the terminal.

#### Responsibilities

- Render game information as text.
- Support ASCII-based visualizations.
- Read user input from the terminal.
- Display prompts, errors, turns, and results.

#### Use cases

- Local debugging.
- Simple human play.
- Prototypes.
- Educational examples.

---

### Concrete interface: `StreamlitInterface`

An interface based on Streamlit, the Python library for building interactive web apps.

#### Responsibilities

- Render the game state through Streamlit components.
- Collect user decisions through Streamlit widgets.
- Provide a browser-based interface without requiring a separate frontend.
- Manage interaction state as needed by Streamlit.

#### Use cases

- Web-based demos.
- Internal tools.
- Interactive notebooks or teaching interfaces.
- Quick prototypes for human interaction.

---

### Concrete interface: `HTMLInterface`

An interface that generates HTML directly from Python.

#### Responsibilities

- Produce HTML representations of the game state.
- Allow the game to be displayed in a web context.
- Separate rendering from game logic.
- Potentially integrate with a custom web server or frontend.

#### Use cases

- Custom web applications.
- Static or dynamic HTML rendering.
- More control than Streamlit over layout and presentation.

---

## 5. Module: `view`

The view module is responsible for deciding what information should be shown to a human player and how it should be represented through a given interface.

The view is not the same as the interface.

- The interface defines the communication medium.
- The view defines the game-specific presentation.

### Main responsibility

Transform a game state into information that a player can understand and use to make a decision.

### Abstract class: `View`

Represents the visual or textual representation of a game state.

#### Responsibilities

- Decide what part of the state is visible to a given player.
- Adapt the state representation to the active interface.
- Present legal moves or relevant decision information.
- Hide private information when required.
- Provide human-readable descriptions of states and moves.
- Help human players understand the current position.

#### Possible methods

```python
class View:
    def render_state(self, state: GameState, player: "Player", interface: Interface) -> None:
        ...

    def render_legal_moves(
        self,
        state: GameState,
        player: "Player",
        legal_moves: list[Move],
        interface: Interface,
    ) -> None:
        ...

    def parse_move(self, raw_input: str, state: GameState, player: "Player") -> Move:
        ...
```

#### Notes

The view is especially important for human players.

For automatic players, the view may be unnecessary because they can choose moves directly from the game state.

---

## 6. Module: `player`

The player module defines the entities that choose moves.

A player is any object that, given a position, decides which move to perform.

### Main responsibility

Select a move from a game state.

### Abstract class: `Player`

Base contract for all types of players.

#### Responsibilities

- Receive the current game state or the information available to that player.
- Decide which move to make.
- Return a valid `Move` object.
- Support both human and automatic decision-making.

#### Core method

```python
class Player:
    def choose_move(self, state: GameState) -> Move:
        ...
```

---

### Concrete class: `HumanPlayer`

A player controlled by a human.

#### Responsibilities

- Use a `View` to display the relevant game information.
- Use an `Interface` to interact with the human user.
- Ask the user for a decision.
- Convert the user's input into a `Move`.
- Return the selected move to the engine.

#### Typical dependencies

```python
class HumanPlayer(Player):
    view: View
    interface: Interface
```

#### Basic behavior

```python
class HumanPlayer(Player):
    def choose_move(self, state: GameState) -> Move:
        self.view.render_state(state, self, self.interface)
        raw_input = self.interface.ask("Choose a move: ")
        return self.view.parse_move(raw_input, state, self)
```

#### Notes

Human players need interaction with the view because they require information to be presented in a readable format.

---

### Concrete class: `AutomaticPlayer`

A player controlled by an algorithm.

#### Responsibilities

- Choose a move without human interaction.
- Operate directly on the current state or observation.
- Support bots, heuristics, random agents, AI agents, or search algorithms.

#### Examples

- Random player.
- Greedy player.
- Minimax player.
- Monte Carlo Tree Search player.
- Reinforcement learning agent.

#### Notes

Automatic players may not need a view or interface. They can be used with `NullInterface` for simulations.

---

## 7. Overall interaction flow

The intended flow is:

1. A concrete game defines its configuration, rules, state, and moves.
2. An engine is created with:
   - Game rules.
   - Initial game state.
   - List of players.
   - Interface.
3. The engine starts the game loop.
4. On each turn:
   - The engine identifies the active player.
   - The engine asks that player to choose a move.
   - If the player is human, the player uses a view and interface.
   - If the player is automatic, the player may choose directly from the state.
   - The engine applies the move through the rules.
   - The state is updated.
5. The loop ends when the rules determine that the state is terminal.
6. The final result is calculated and returned.

---

## 8. Suggested package structure

```text
project/
│
├── game/
│   ├── __init__.py
│   ├── config.py        # GameConfig
│   ├── rules.py         # GameRules
│   ├── state.py         # GameState
│   └── move.py          # Move
│
├── engine/
│   ├── __init__.py
│   └── engine.py        # Engine
│
├── interface/
│   ├── __init__.py
│   ├── base.py          # Interface
│   ├── null.py          # NullInterface
│   ├── terminal.py      # TerminalInterface
│   ├── streamlit.py     # StreamlitInterface
│   └── html.py          # HTMLInterface
│
├── view/
│   ├── __init__.py
│   └── base.py          # View
│
└── player/
    ├── __init__.py
    ├── base.py          # Player
    ├── human.py         # HumanPlayer
    └── automatic.py     # AutomaticPlayer
```

---

## 9. Responsibility summary

| Module | Class | Responsibility |
|---|---|---|
| `game` | `GameConfig` | Static configuration of a concrete game. |
| `game` | `GameRules` | Legal moves, transitions, terminal states, and results. |
| `game` | `GameState` | Dynamic representation of the current game position. |
| `game` | `Move` | Representation of a player's action. |
| `engine` | `Engine` | Runs the turn-based game loop. |
| `interface` | `Interface` | Common contract for external interaction. |
| `interface` | `NullInterface` | Empty interface for simulations or automatic players. |
| `interface` | `TerminalInterface` | ASCII/text interaction through the terminal. |
| `interface` | `StreamlitInterface` | Web interaction through Streamlit. |
| `interface` | `HTMLInterface` | HTML generation from Python. |
| `view` | `View` | Presents game information to human players depending on the interface. |
| `player` | `Player` | Base class for any object that selects a move from a position. |
| `player` | `HumanPlayer` | Human-controlled player using a view and interface. |
| `player` | `AutomaticPlayer` | Algorithm-controlled player that may not need a view or interface. |

---

## 10. Design principles

### Separation of concerns

Each module has a distinct responsibility:

- `game` defines what the game is.
- `engine` defines how the game is executed.
- `interface` defines how interaction happens.
- `view` defines what information is shown.
- `player` defines who or what chooses moves.

### Game independence

The framework should not assume a specific game structure such as a board, cards, dice, scores, or two-player zero-sum logic.

### Turn-based assumption

The only required assumption is that the game advances through turns.

### Human and automatic compatibility

The same game and engine should support:

- Human vs human.
- Human vs AI.
- AI vs AI.
- Multi-player games.
- Simulations with no interface.

### Interface independence

Game logic should not depend on the terminal, Streamlit, HTML, or any other rendering technology.

### View-interface distinction

The view decides what game information should be shown.

The interface decides how that information is communicated.

---

## 11. Minimal abstract skeleton

```python
from abc import ABC, abstractmethod
from typing import Any


class GameConfig(ABC):
    """Static configuration for a concrete game."""
    pass


class Move(ABC):
    """Action selected by a player."""
    pass


class GameState(ABC):
    """Dynamic state of the game."""

    @abstractmethod
    def current_player_id(self) -> Any:
        pass


class GameRules(ABC):
    """Rules and transition logic for a concrete game."""

    @abstractmethod
    def legal_moves(self, state: GameState) -> list[Move]:
        pass

    @abstractmethod
    def apply_move(self, state: GameState, move: Move) -> GameState:
        pass

    @abstractmethod
    def is_terminal(self, state: GameState) -> bool:
        pass

    @abstractmethod
    def result(self, state: GameState) -> Any:
        pass


class Interface(ABC):
    """Base class for interaction mechanisms."""

    def render(self, content: str) -> None:
        pass

    def ask(self, prompt: str) -> str:
        raise NotImplementedError("This interface does not support input.")


class NullInterface(Interface):
    """Interface that performs no input/output."""
    pass


class TerminalInterface(Interface):
    """Terminal-based ASCII/text interface."""

    def render(self, content: str) -> None:
        print(content)

    def ask(self, prompt: str) -> str:
        return input(prompt)


class View(ABC):
    """Presentation layer for human-readable game information."""

    @abstractmethod
    def render_state(self, state: GameState, player: "Player", interface: Interface) -> None:
        pass

    @abstractmethod
    def parse_move(self, raw_input: str, state: GameState, player: "Player") -> Move:
        pass


class Player(ABC):
    """Base class for any entity that chooses moves."""

    @abstractmethod
    def choose_move(self, state: GameState) -> Move:
        pass


class HumanPlayer(Player):
    """Human-controlled player using a view and interface."""

    def __init__(self, view: View, interface: Interface):
        self.view = view
        self.interface = interface

    def choose_move(self, state: GameState) -> Move:
        self.view.render_state(state, self, self.interface)
        raw_input = self.interface.ask("Choose a move: ")
        return self.view.parse_move(raw_input, state, self)


class AutomaticPlayer(Player):
    """Algorithm-controlled player."""

    def choose_move(self, state: GameState) -> Move:
        raise NotImplementedError


class Engine:
    """Runs the turn-based game loop."""

    def __init__(
        self,
        rules: GameRules,
        initial_state: GameState,
        players: list[Player],
        interface: Interface,
    ):
        self.rules = rules
        self.state = initial_state
        self.players = players
        self.interface = interface

    def get_current_player(self) -> Player:
        player_id = self.state.current_player_id()
        return self.players[player_id]

    def run(self):
        while not self.rules.is_terminal(self.state):
            player = self.get_current_player()
            move = player.choose_move(self.state)
            self.state = self.rules.apply_move(self.state, move)

        return self.rules.result(self.state)
```
