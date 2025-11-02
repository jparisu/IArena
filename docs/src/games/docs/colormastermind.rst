.. _colormastermind_docs:

################
Color Mastermind
################

.. figure:: /resources/images/mastermind.png
    :scale: 8%

This game is the classical Mastermind game as 1 player version.
The objective of the game is to guess the *secret code*, this is a sequence of *N* colors (strings) chosen from *M* colors available.
Each turn the player has to guess the code.
After each guess, the game will tell the player which of the guesses appears in the code but are not correctly positioned, and which ones are correctly positioned.
The goal is to guess the code in the fewest number of turns.

Some changes have been made to the original game:

- There is only one player (guesser) while the other player (password-maker) is not considered a player.
- Colors are represented by strings.
- There are 2 versions: **with repetitions** (same color could appear more than once in the code) and **without repetitions**.

An online version of the game can be found at `this link <https://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/guess.html>`_.


.. note::

  This game is very similar to `Wordle <wordle_docs>` game, with the difference that the feedback is not given per position but as a total of correct and misplaced values.


====
Goal
====

Guess the correct *secret code* in the fewest number of turns.

-----
Score
-----

The score is ``-T`` where ``T`` is the number of turns needed to guess the secret code.
The highest the score, the better.


======
Import
======

.. code-block:: python

  from IArena.games.ColorMastermind import ColorMastermindPosition
  from IArena.games.ColorMastermind import ColorMastermindMovement
  from IArena.games.ColorMastermind import ColorMastermindRules


========
Movement
========

A movement has a *guess* in the format of ``List[str]``.
It must have ``N`` strings.

- ``guess``
    - ``List[str]``
    - ``len == N``
    - Each value is a string representing a color. The available colors are defined by the rules of the game.


.. code-block:: python

  # A guess in a game with N=3
  movement = ColorMastermindMovement(guess=["red", "blue", "green"])

.. warning::

  Depending on the rules, the guess could be invalid if has repeated values (the same number more than once).



========
Position
========

A position is represented by a list of movements (guesses) and a list of feedback.

--------
Feedback
--------

A ``ColorMastermindFeedback`` is an object that contains 2 integer values:

- ``correct``: the number of values in the guess that are correctly placed.
- ``misplaced``: the number of values in the guess that are in the secret code but misplaced.


.. code-block:: python

  # position : ColorMastermindPosition
  guesses = position.guesses()
  feedback = position.feedback()

  guesses[-1]  # Last guess
  guesses[-1][0]  # First position of the last guess

  correct = feedback[-1].correct  # Number of correct values in the last guess
  misplaced = feedback[-1].misplaced  # Number of misplaced values in the last guess


-------
Methods
-------

- ``guesses() -> List[ColorMastermindMovement]``: List of guesses made so far.
- ``feedback() -> List[List[ColorMastermindFeedback]]``: List of feedback lists made so far.
- ``last_guess() -> ColorMastermindMovement``: Last guess made.
- ``last_feedback() -> List[ColorMastermindFeedback]``: Feedback of the last guess.
- ``code_size() -> int``: Number of values in the secret code (N).
- ``number_values() -> int``: Number of different values available (M). If no repetitions allowed, M >= N.
- ``allow_repetition() -> bool``: Whether the secret code can have repeated values.
- ``possible_colors() -> List[str]``: List of possible colors available in the game (no repeated values).


=====
Rules
=====

This object defines the rules of the game, including the secret code.
When constructed, it sets the secret code, the number of values in the code (N), and the number of different values available (M), and whether repetitions are allowed.

Within the rules, the value ``possible_colors_`` is defined, which is a list of different strings representing the available strings in the game.
Each of the strings is meant to represent a different color.
However, no required format is imposed on the strings, so they can be any string values, as long as it is that each value belongs to the possible values given by ``possible_colors()``.


-------
Methods
-------

- ``code_size() -> int``: Number of values in the secret code (N).
- ``number_values() -> int``: Number of different values available (M). If no repetitions allowed, M >= N.
- ``allow_repetition() -> bool``: Whether the secret code can have repeated values.
- ``possible_colors() -> List[str]``: List of possible colors available in the game.


-----------
Constructor
-----------

Arguments for constructor are:

- ``code_size: int``: N
- ``number_values: int``: M
- ``possible_colors: List[str]``: List of M different strings representing the possible colors.
- ``secret: List[str]``: List of N values in ``possible_colors`` representing the secret code.
- ``allow_repetition: bool``: Whether the secret code can have repeated values.


1. Using a secret code already defined.

  .. code-block:: python

    # Secret code with N=4 and M=6
    rules = ColorMastermindRules(
        code_size=4,
        number_values=6,
        possible_colors={"a", "b", "c", "d", "e", "f"},
        secret=["a", "b", "c", "d"],
        allow_repetition=False
    )


Default Colors
^^^^^^^^^^^^^^

There is a function ``ColorMastermindRules.default_colors(number_values: int) -> List[str]`` that returns a list of default colors (strings) for a given ``M``.

  .. code-block:: python

    from IArena.games.ColorMastermind import ColorMastermindRules

    colors = ColorMastermindRules.default_colors(6)
    print(colors)  # Output: {'red', 'blue', 'green', 'yellow', 'orange', 'purple'}



.. _Colormastermind_playable_player:
