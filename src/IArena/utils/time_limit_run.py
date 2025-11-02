from typing import Any, Callable, Dict, Optional, Tuple
import threading
import queue
import sys

class TimeLimitExpired(TimeoutError):
    pass

def time_limit_run(
    func: Callable[..., Any],
    timeout_s: float,
    args: Tuple[Any, ...] = (),
    kwargs: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Run `func(*args, **kwargs)` in a thread and wait up to `timeout_s` seconds.

    - Returns the function's result on success.
    - Propagates the function's exception (with original traceback).
    - Raises TimeLimitExpired on timeout (the worker thread may keep running).
    """
    if kwargs is None:
        kwargs = {}

    q: "queue.Queue[tuple[str, Any]]" = queue.Queue(maxsize=1)

    def worker():
        """
        Worker function to execute the target function and store its result or exception.

        Results are put into the queue as a tuple:
        - (True, result) on success
        - (False, (exception, traceback)) on failure
        """
        try:
            rv = func(*args, **kwargs)
            q.put((True, rv))
        except BaseException as e:
            # Preserve original traceback across the thread boundary
            _, exc, tb = sys.exc_info()
            q.put((False, (exc, tb)))

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    t.join(timeout_s)

    if t.is_alive():
        # Thread continues in background (by design); we only time out.
        raise TimeLimitExpired(f"Timeout of {timeout_s} seconds exceeded")

    # Thread finished; fetch result or exception
    try:
        ok, payload = q.get_nowait()
    except queue.Empty:
        # Extremely unlikely, but treat as abnormal termination
        raise RuntimeError("Worker finished without producing a result.")

    if ok:
        return payload
    else:
        exc, tb = payload
        # Re-raise original exception with its traceback
        raise exc.with_traceback(tb)
