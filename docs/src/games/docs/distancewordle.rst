.. _distancewordle_docs:

###############
Distance Wordle
###############

.. figure:: /resources/images/wordle.png
    :scale: 30%

This game is a version of the New York Times game Wordle, as 1 player guess game.
The objective of the game is to guess the *secret code*, this is a sequence of *N* numbers (letters in the actual game) chosen from *M* numbers available ``[0,M)``.
Each turn the player has to guess the code.
After each guess, the game will tell the player how far each of the guesses is from the correct position.
The goal is to guess the code in the fewest number of turns.

Some changes have been made to the original game:

- Instead of letters and words we use numbers.
- There are 2 versions: **with repetitions** (same number could appear more than once in the code) and **without repetitions**.

The online version of the game can be found at `this link <https://www.nytimes.com/games/wordle/index.html>`_.
Be aware that this version differ from the game implemented here as explained before.


=======================
Differences with Wordle
=======================

This game is a version of the game :ref:`wordle_docs`, with the following differences:

- The **feedback** is no longer a list with `0s`, `1s` and `2s`, but a list of integers representing the absolute distance between the guessed value and its correct position in the secret code.

For example, a feedback of ``[0, 1, 3]`` means that:

- The first value is correct (distance ``0``).
- The second value is in the secret code, but misplaced by ``1`` position.
- The third value is not in the secret code, a distance equal or higher ``3`` in a code of size ``3`` means that the value is not present.



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

  from IArena.games.DistanceWordle import DistanceWordlePosition
  from IArena.games.DistanceWordle import DistanceWordleMovement
  from IArena.games.DistanceWordle import DistanceWordleRules


========
Movement
========

A movement has a *guess* in the format of ``List[int]``.
It must have ``N`` integers in the range ``[0,M)``.

- ``guess``
    - ``List[int]``
    - ``len == N``
    - ``0 <= l[i] < M``
    - Guess of the secret code


.. code-block:: python

  # A guess in a game with N=3 and M>2
  movement = DistanceWordleMovement(guess=[0, 1, 2])

.. warning::

  Depending on the rules, the guess could be invalid if has repeated values (the same number more than once).


========
Position
========

A position is represented by a list of movements (guesses) and a list of feedback.

--------
Feedback
--------

The feedback of a guess is a list of ``int`` indicating for each of the values in the guess,
if it is correctly placed (``0``),
if it is in the secret code, but misplaced (``X``),
or whether it is not present in the secret code (``-1``).
``X`` is the absolute difference between the guessed value and this value correct position.

.. code-block:: python

  # position : DistanceWordlePosition
  guesses = position.guesses()
  feedback = position.feedback()

  guesses[-1]  # Last guess
  guesses[-1][0]  # First position of the last guess

  feedback[-1]  # Feedback of the last guess
  c = feedback[-1][0]  # Feedback of the first position of the last guess

  if c == 0:
    # The first value of the last guess is correct
  elif c == 1:
    # The first value of the last guess is in the code to the left or right by 1
  elif c == 2:
    ...
  elif c == -1:
    # The first value of the last guess is not in the actual code


For example, let's imagine an scenario where ``N=4``, ``M=6``, the secret code is ``[1, 3, 5, 4]``.
If the player makes the guess ``[1, 4, 3, 0]``, the feedback will be ``[0, 2, 1, 4]``.

- The first value ``1`` is correct, so the distance to its real position is ``0``.
- The second value ``4`` is in the secret code, but misplaced, it should be in forth position, so the distance is ``2``.
- The third value ``3`` is in the secret code, but misplaced, it should be in second position, so the distance is ``1``.
- The forth value ``0`` is not in the secret code, so the feedback is ``N``.




-------
Methods
-------

- ``guesses() -> List[DistanceWordleMovement]``: List of guesses made so far.
- ``feedback() -> List[List[int]]``: List of feedback lists made so far.
- ``last_guess() -> DistanceWordleMovement``: Last guess made.
- ``last_feedback() -> List[int]``: Feedback of the last guess.
- ``code_size() -> int``: Number of values in the secret code (N).
- ``number_values() -> int``: Number of different values available (M). If no repetitions allowed, M >= N.
- ``allow_repetition() -> bool``: Whether the secret code can have repeated values.

=====
Rules
=====

This object defines the rules of the game, including the secret code.
When constructed, it sets the secret code, the number of values in the code (N), and the number of different values available (M), and whether repetitions are allowed.



-------
Methods
-------

- ``code_size() -> int``: Number of values in the secret code (N).
- ``number_values() -> int``: Number of different values available (M). If no repetitions allowed, M >= N.
- ``allow_repetition() -> bool``: Whether the secret code can have repeated values.


-----------
Constructor
-----------

Arguments for constructor are:

- ``code_size: int``: N
- ``number_values: int``: M
- ``secret: List[int]``: List of N values between ``[0,M)`` representing the secret code.
- ``allow_repetition: bool``: Whether the secret code can have repeated values.


1. Using a secret code already defined.

  .. code-block:: python

    # Secret code with N=4 and M=6
    rules = DistanceWordleRules(
        code_size=4,
        number_values=6,
        secret=[0, 1, 2, 3],
        allow_repetition=False
    )
