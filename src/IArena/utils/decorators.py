
def unsupported(f):
    """Decorator for marking functions as not implemented."""
    def decorator(*args, **kwargs):
        raise NotImplementedError(
            f'Function <{f.__name__}> is not implemented.')
    return decorator


def pure_virtual(f):
    """Decorator for marking functions as pure virtual."""
    def decorator(*args, **kwargs):
        raise NotImplementedError(
            f'Function <{f.__name__}> '
            'must be implemented from a child class.')
    return decorator

def override(f):
    """
    Decorator for marking functions as override.

    note: Do nothing but help readability.
    """
    def decorator(*args, **kwargs):
        return f(*args, **kwargs)
    return decorator
