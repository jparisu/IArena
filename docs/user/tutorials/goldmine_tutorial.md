# Tutorial: Learning the IArena Framework with GoldMine

This tutorial uses **GoldMine** as the main example to explain how to work with the **IArena** framework step by step. The goal is not only to make GoldMine run, but also to understand the role of each framework component: **configuration**, **rules**, **positions**, **movements**, **players**, and **arenas**.

GoldMine is a good teaching example because it is a **single-player search game** with a clear flow:

1. define a configuration,
2. create the rules,
3. inspect a position,
4. build a movement,
5. define a dummy player,
6. run the game inside an arena.

We encourage to check the [Getting started](../../getting_started.md) guide before this tutorial, as it covers the basic concepts of the framework.
For further details on game structure refer to [Game Overview](../../user/games/games.md) and for more on players refer to [Playing](../../user/playing/playing.md).

If you want to contribute to the library or implement deeper features, refer to [API section](../../api/index.md).


# GoldMine

The game **GoldMine** is a single-player search.
The goal of the game is to navigate a square grid from a start position, digging adjacent tiles to find gold.
Each tile has a digging cost, and the player can only see the costs of adjacent tiles.
The gold is hidden in one of the tiles, and the player must find it while minimizing the total digging cost.

To specific implementation details, check [GoldMine documentation](../../user/games/goldmine.md).

---

# 0. Installation

IArena is a Python package hosted in github that can be installed with pip:

```bash
pip install git+https://github.com/jparisu/iarena.git
```

For further detail, refer to the [installation documentation](../../installation.md).

---

# 1. Create a Configuration

The **configuration** is the static description of the game instance. In GoldMine, it defines the map size, the start and target positions, optional hint systems, and how the map is created. Without a configuration, the framework does not know what game world to build.

Check [Configuration documentation](../../user/games/goldmine.md#2-configuration-goldmineconfiguration) for further information.

---

### 1.1 Create a Configuration with a Manual Matrix

A configuration may be created by directly providing a matrix that defines the map.
This matrix defines how much it costs to dig each tile, and the framework will use it as the basis for the game world.

Let's create a 3x3 grid map where we start in the top-left corner and the gold is in the bottom-right corner.

```python

from iarena.gaming.goldmine import GoldMineConfiguration

manual_map = [
    [0.0, 2.0, 3.0],
    [4.0, 1.5, 2.5],
    [3.5, 2.0, 1.0],
]

configuration = GoldMineConfiguration(
    start=(0, 0),               # Starting position (row, col). By default, top-left corner
    target=(2, 2),              # Target position (row, col)
    map_data=manual_map,        # Matrix defining the map costs
)

print(f"Configuration created successfully {configuration}")
```

!!! note
    The initial tile should be 0.0. Otherwise, the initial cost is non-zero.


---

### 1.2 Create a Configuration with a Random Map

This game is commonly played with an unknown map, where the cost of the tiles is only revealed when the player digs the adjacent tiles.
There are several configurations in order to generate random maps.

Let's create a configuration with a random 4x4 map, where the start is in the top-left corner.
If not set, the gold cell will also be randomly generated and hidden for the player.

```python
random_configuration = GoldMineConfiguration(
    n_rows=4,
    n_cols=4,
    start=(0, 0),
    map_generator="uniform",
    seed=0,
)

print(f"Configuration with random map created successfully {random_configuration}")
```

For a more detailed explanation on how maps are generated, check the [map generation documentation](../../user/games/squaremap.md).

---

# 2. Create Rules

So far we have only created configurations.
This configurations are used to create the rules of a new game.

The **Rules** object is the engine of the game. It knows how to generate the initial position, what movements are legal, how positions evolve after moves, when the game finishes, and how scoring works. In IArena, this is one of the most important abstractions, because it transforms a static configuration into a playable system.

Let's create a `Rules` object.
Depending on the configuration used, the internal map and gold position will differ.
Try using both previous configurations to see how the rules adapt to different game instances.

```python
from iarena.gaming.goldmine import GoldMineRules

rules = GoldMineRules(configuration)

print("Rules created successfully")
print(f" - Test rules: Number of players: {rules.n_players()}")
```

The player do not have access to the internal Rules information.
This means that `GoldMineRules` does not expose many important information, as the initial position, the target position, the map, etc.

For debugging purposes, there is a function that shows graphically the state of the game.
Let's use the first position of the game to see how the map looks like and where the gold is hidden:

```python
rules._generate_plot_position(rules.first_position()).show()
```

Check [Rules documentation](../../user/games/goldmine.md#34-goldminerules) for further information.

---

# 3. Get a Position and Read Its Values

A **Position** is the current game state from the point of view of the player.
In GoldMine, the position does not expose the entire hidden world directly.
Instead, it provides methods to inspect the information that the player is allowed to know, such as valid directions, movement costs, compass hints, and current accumulated cost.

The first position is obtained from the rules object.
From it, the player would be able to ask for valid directions, costs, and hints, but not for the internal map or the gold position.

```python
from iarena.gaming.goldmine import GoldMinePosition

first_position = rules.first_position()

print("Initial position created")
print(f"Current accumulated cost: {first_position.get_current_cost()}")

valid_directions = list(first_position.get_valid_directions())
print(f"Valid directions: {valid_directions}")

print("Directions with costs:")
for direction, cost in first_position.get_directions_with_cost():
    print(f"  - {direction}: {cost}")
```

Check [Position documentation](../../user/games/goldmine.md#32-goldmineposition) for further information.

---

# 4. Create a Movement

A **Movement** is an action chosen by the player.
In GoldMine, a movement is simply one cardinal direction represented through `GoldMineMovement`, which internally uses `SquareMapDirection`.
This separation is important in the framework because a movement is the formal object passed to the rules when advancing the game.

Let's create a movement that moves RIGHT.
First, let's check if this movement is legal from the first position.
Then let's apply it to see how the position evolves.
As the position does not expose the internal map, we will use again the rules plot method to see the effect of the movement.

```python
from iarena.gaming.goldmine import GoldMineMovement
from iarena.utilizing.mapping.square_map.SquareMapDirection import SquareMapDirection

move = GoldMineMovement(direction=SquareMapDirection.RIGHT)
print(f"Movement created: {move}")

is_legal = move in rules.possible_movements(first_position)
print(f"Is the movement legal? {is_legal}")

second_position = rules.next_position(first_position, move)
print(f"Second position created successfully after applying movement {move}")
rules._generate_plot_position(second_position).show()
```

!!! note
    Note that the tiles already dug do not have cost anymore.
    The player can now move along already dug tiles without additional cost.


Check [Movement documentation](../../user/games/goldmine.md#33-goldminemovement) for further information.


---

# 5. Create a Specific Dummy Player

A **Player** is an agent that receives a position and returns a movement.
In IArena, players are the decision-making components.

The example below defines a simple player that always tries to move **RIGHT** when possible; otherwise, it chooses the first available movement.

```python
from iarena.playing import Player

class AlwaysRightGoldMinePlayer(Player):

    def play(self, position: GoldMinePosition) -> GoldMineMovement:
        possible_movements = list(position.get_valid_directions())
        # Note: we convert the iterator to a list for simplicity

        for direction in possible_movements:
            if direction == SquareMapDirection.RIGHT:
                print(f"[{self.name()}] Choosing RIGHT")
                return GoldMineMovement(direction)

        fallback = list(possible_movements)[0]
        print(f"[{self.name()}] RIGHT not available, choosing {fallback}")
        return GoldMineMovement(direction=fallback)

player = AlwaysRightGoldMinePlayer()
print(f"Player created successfully: {player.name()}")
```

For this player, let's test how it would perform in the first position of the game:

```python
print(f"Testing player {player.name()} in the first position")
movement_chosen = player.play(first_position)
print(f"Player chose movement: {movement_chosen.direction}")
```

Check [Player documentation](../../user/playing/playing.md) for further information.

---

# 6. Create an Arena to Test the Player

The **Arena** is the execution environment that runs the game loop.
It is the central execution point between rules and players.
This is where the complete game loop happens: the arena asks the player for movements, applies the rules, stops when the game is finished, and returns the final score.

Let's create an arena to test our previous player in the GoldMine game:

```python
from iarena.arening import ArenaFactory

arena = ArenaFactory.create_arena(
    max_turns=15,       # Maximum number of turns to prevent infinite loops
)

# Run the game and get the final scoreboard
scoreboard = arena.play(
    rules=rules,        # Game rules
    players=[player],   # List of players (in this case, only one)
)

print("Game finished")
print(f"Final score: {scoreboard.get_score(0)}")
```

!!! Warning
    At this point the game would stop with an Exception because the maximum number of turns is reached.
    Try to implement a smarter player that is able to find the gold within the maximum number of turns.

---

# 7. Future Steps

## Step by step Game

IArena provides a `View` that allows the user to see the game step by step.
This is useful to understand the flow of the game and debug players.

!!! note
    This `View` classes depend on each game, so other games may not implement this feature.

For this, when creating an `Arena`, using the specific `GoldMineTerminalView` view:

```python
from iarena.gaming.goldmine.GoldMineTerminalView import GoldMineTerminalView

# Run the game and get the final scoreboard
scoreboard = arena.play(
    rules=rules,        # Game rules
    players=[player],   # List of players (in this case, only one)
    view=GoldMineTerminalView(),
)

print(f"Final score: {scoreboard.get_score(0)}")
```


## Terminal Player

IArena provides an already implemented player that is able to play through terminal input.
This is `PolyvalentTerminalPlayer`, which can be used to play GoldMine manually.

Let's try to play GoldMine with a human player by terminal input:

```python
from iarena.playing import PolyvalentTerminalPlayer

human_player = PolyvalentTerminalPlayer()

# Run the game and get the final scoreboard
scoreboard = arena.play(
    rules=rules,        # Game rules
    players=[human_player],   # List of players (in this case, only one)
)
print(f"Final score: {scoreboard.get_score(0)}")
```


## Player memory implementation

A `Player` object should be able to play several games in a row.
In order to keep a clean internal state that rests for each game, the `Player` class has a `starting_game` method that is called at the beginning of each game.

Let's create a player that keeps the number of steps taken so far:

```python
class MemoryGoldMinePlayer(Player):

    def __init__(self, name: str):
        super().__init__(name)
        self.steps = 0

    def starting_game(self, rules: GoldMineRules, player_index: int) -> None:
        self.steps = 0

    def play(self, rules, position):
        # Update the number of steps
        self.steps += 1

        # Select next movement
        ...
        # return movement
```


## Hints

GoldMine has a hint system that is enabled through the configuration.
This system gives the player some information that may help the player to find the gold faster.
There are 3 main systems:

### Compass

The compass gives the player the direction where the gold is located with respect to the current position.

Let's see an example on how to create a `Rules` object with the compass enabled, and how to use it from the position:

```python
# Create a configuration with the compass activated
configuration_with_compass = GoldMineConfiguration(
    n_rows=4,
    n_cols=4,
    start=(0, 0),
    target=(3, 3),
    map_generator="uniform",
    seed=0,
    compass_activated=True,
)
rules_with_compass = GoldMineRules(configuration_with_compass)
print(f"Compass activated: {rules_with_compass.compass_activated()}")

# Get the first position and check the compass hint
first_position_with_compass = rules_with_compass.first_position()
compass_hint = first_position_with_compass.get_compass()
print(f"Compass hint: {compass_hint}")
```

### Proximity

The proximity hint gives the player the Manhattan distance to the gold from the current position.

Let's see an example on how to create a `Rules` object with the proximity hint enabled, and how to use it from the position:

```python
# Create a configuration with the proximity hint activated
configuration_with_proximity = GoldMineConfiguration(
    n_rows=4,
    n_cols=4,
    start=(0, 0),
    target=(3, 3),
    map_generator="uniform",
    seed=0,
    proximity_activated=True,
)
rules_with_proximity = GoldMineRules(configuration_with_proximity)
print(f"Proximity hint activated: {rules_with_proximity.proximity_activated()}")

# Get the first position and check the proximity hint
first_position_with_proximity = rules_with_proximity.first_position()
proximity_hint = first_position_with_proximity.get_proximity()
print(f"Proximity hint: {proximity_hint}")
```

### Heuristic

The heuristic hint gives the player an estimation of the cost to reach the gold from the current position.
This estimation may reduce as long as the player gets closer to the gold.
However, this may not be necessarily accurate.

For more detailed information regarding hints, check the [GoldMine configuration documentation](../../user/games/goldmine.md#hints-and-heuristics).
