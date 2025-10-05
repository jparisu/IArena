import signal
import threading
from contextlib import contextmanager
from typing import Any, Callable, Dict, Optional, Tuple

class TimeLimitExpired(TimeoutError):
    pass

@contextmanager
def _alarm_after(timeout_s: Optional[float]):
    if timeout_s is None:
        yield
        return
    if threading.current_thread() is not threading.main_thread():
        raise RuntimeError("time_limit_run requires the main thread when using SIGALRM.")
    if not hasattr(signal, "setitimer"):
        raise RuntimeError("This platform doesn't support setitimer/SIGALRM (Windows).")

    old_handler = signal.getsignal(signal.SIGALRM)
    old_timer = signal.getitimer(signal.ITIMER_REAL)

    def _raise_timeout(signum, frame):
        raise TimeLimitExpired(f"Call timed out after {timeout_s} seconds.")

    try:
        signal.signal(signal.SIGALRM, _raise_timeout)
        signal.setitimer(signal.ITIMER_REAL, timeout_s, 0.0)
        yield
    finally:
        # cancel ours
        signal.setitimer(signal.ITIMER_REAL, 0.0, 0.0)
        signal.signal(signal.SIGALRM, old_handler)
        # restore previous timer if it existed
        if old_timer[0] > 0 or old_timer[1] > 0:
            signal.setitimer(signal.ITIMER_REAL, *old_timer)

def time_limit_run(
    func: Callable[..., Any],
    args: Tuple[Any, ...] = (),
    kwargs: Optional[Dict[str, Any]] = None,
    *,
    timeout_s: Optional[float] = None,
    return_on_timeout: Any = None,
    raise_on_timeout: bool = True,
) -> Any:
    if kwargs is None:
        kwargs = {}
    try:
        with _alarm_after(timeout_s):
            return func(*args, **kwargs)
    except TimeLimitExpired:
        if raise_on_timeout:
            raise TimeoutError(f"Call timed out after {timeout_s} seconds.")
        return return_on_timeout
