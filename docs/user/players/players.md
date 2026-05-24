# Players

Players implement the strategy layer of IArena.

## Player Interface

`iarena.playing.Player.Player` defines two required methods:

- `play(pos) -> Movement`
- `starting_game(rules, player_index) -> None`

It also implements `Recognizable`, so concrete players expose `name()`.


### PlayerIndex

`PlayerIndex` is a simple wrapper around an integer that identifies the player in the game. It is used to determine which player's turn it is and to access the corresponding score from the `ScoreBoard`.

## Picking Movements

A player usually asks the rules for legal moves:

```python
possible = list(pos.get_rules().possible_movements(pos))
```

Then selects one movement according to its strategy.

## Built-in Player Types

- `PolyvalentRandomPlayer`: generic random strategy across games.
- `PolyvalentTerminalPlayer`: human input through terminal views.
- `PolyvalentStreamlitPlayer`: human input through Streamlit views.
- `LoadPlayer`: loader/wrapper player utility.

## Example

```python
from iarena.playing.PolyvalentRandomPlayer import PolyvalentRandomPlayer

player = PolyvalentRandomPlayer()
```

See also: [Random Player](random.md).
