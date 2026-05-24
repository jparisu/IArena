# Random Player

`PolyvalentRandomPlayer` is a reusable player that works with any game exposing legal movements through `Rules.possible_movements`.

## Behavior

- On `starting_game`, it stores runtime context and initializes a `RandomGenerator`.
- On `play`, it lists legal movements from the current position and returns one uniformly at random.
- If no legal movement exists, it raises `ValueError`.

## Import

```python
from iarena.playing.PolyvalentRandomPlayer import PolyvalentRandomPlayer
```
