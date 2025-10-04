from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

def time_limit_run(timeout_s: float, func, *args, **kwargs):
    """
    Run a function with a time limit in a worker thread.
    Exceptions raised by `func` are propagated with their original traceback.
    Raises TimeoutError if the timeout is exceeded.
    """
    with ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(func, *args, **kwargs)
        try:
            return fut.result(timeout=timeout_s)  # re-raises func's exceptions
        except FuturesTimeout:
            # Best effort: this won't stop code already running in C extensions.
            fut.cancel()
            raise TimeoutError(f"Timeout of {timeout_s} seconds exceeded")
