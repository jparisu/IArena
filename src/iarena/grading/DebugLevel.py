"""Defines debug verbosity levels used during grading execution flows."""

from enum import Enum


class DebugLevel(Enum):
    """Debug level for trial execution with increasing verbosity.

    Purpose:
        Standardize verbosity selection across grading routines.
    How it is used:
        Grading coordinators consume this enum to decide how much runtime
        information should be emitted while running matches and trials.
    Why it exists:
        Makes logging and diagnostics policy explicit and type-safe for
        trial, exam, and autograder integrations.
    """

    NONE = 0
    ERROR = 1
    WARNING = 2
    USER = 3
    INFO = 4
    DEBUG = 5
