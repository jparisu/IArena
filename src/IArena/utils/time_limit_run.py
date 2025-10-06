from typing import Any, Callable, Dict, Optional, Tuple

import threading

def time_limit_run(
        func: callable,
        timeout_s: float,
        args: Tuple[Any, ...] = (),
        kwargs: Optional[Dict[str, Any]] = None):
    """
    Run a function with a time limit.
    :param time_s: Time limit in seconds.
    :param f: Function to run.
    :param args: Arguments of the function.
    :param kwargs: Keyword arguments of the function.
    :return: The result of the function.
    """
    # Function to return the result as a parameter
    def func_wrapper(result):
        result.append(func(*args, **kwargs))

    # List for the result of the function
    result = []

    # Thread with timeout
    thread = threading.Thread(target=func_wrapper, args=(result,))
    thread.start()
    thread.join(timeout_s)

    if thread.is_alive():
        raise TimeoutError(f'Timeout of {timeout_s} seconds exceeded')
    else:
        if result:
            return result[0]
        else:
            return None
