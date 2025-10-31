
class LimitExceededError(Exception):
    """Exception raised when a limit is exceeded."""
    pass

class ShouldNotHappenError(Exception):
    """Exception raised for situations that should not occur."""
    pass
