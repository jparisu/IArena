"""Defines the primitive score value type used across arenas."""


class Score(float):
    """Primitive wrapper for a score value where higher is better.

    Purpose:
        Define a canonical scalar score type used by the scoring subsystem.
    How it works:
        Extends `float` to make score semantics explicit in method signatures and APIs.
    Used for:
        Representing player outcomes and score limits across arenas and rules engines.
    API:
        This class currently exposes the native `float` API and does not add new public methods.
    Public Attributes:
        None declared at class level in this base definition.
    """
