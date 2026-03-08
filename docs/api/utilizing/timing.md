# Timing

## Timer

::: iarena.utilizing.timing.Timer.Timer
    options:
      show_root_heading: true
      members: true

### Timer Methods

- `Timer.__init__(start_activated: bool = True) -> None`
- `Timer.start() -> None`
- `Timer.pause() -> None`
- `Timer.reset() -> None`
- `Timer.elapsed() -> float`

## Worker

::: iarena.utilizing.timing.Worker.Worker
    options:
      show_root_heading: true
      members: true

### Worker Methods

- `Worker.limited_time_call(func: Callable[..., Any], timeout_s: float, *args: Any) -> Any`
