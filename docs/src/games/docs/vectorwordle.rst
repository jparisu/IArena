.. _vectorwordle_docs:

#############
Vector Wordle
#############

.. figure:: /resources/images/wordle.png
    :scale: 30%

This game is a version of the New York Times game Wordle, as 1 player guess game: `this link <https://www.nytimes.com/games/wordle/index.html>`_.
The objective of the game is to guess the *secret code*, this is a sequence of *N* numbers (letters in the actual game) chosen from *M* numbers available ``[0,M)``.
Each turn the player has to guess the code.
After each guess, the game will tell the player which of the guesses appears in the code but are not correctly positioned, and which ones are correctly positioned.
The goal is to guess the code in the fewest number of turns.

Some changes have been made to the original game:

- Instead of letters and words we use numbers.
- There are 2 versions: **with repetitions** (same number could appear more than once in the code) and **without repetitions**.

The online version of the game can be found at `this link <https://www.nytimes.com/games/wordle/index.htmll>`_.
Be aware that this version differ from the game implemented here as explained before.


=======================
Differences with Wordle
=======================

This game is a version of the game `wordle_docs`, with the following differences:

- Instead of a feedback with values `0`, `1`, `2` (correct position, wrong position, not in code), the feedback is given by 3 different arrays, each of them representing:
    - `positive_feedback() -> List[int]`: List of indexes in the guess that are correct.
    - `misplaced_feedback() -> List[int]`: List of indexes in the guess that are in the code but misplaced.
    - `negative_feedback() -> List[int]`: List of indexes in the guess that are not in the code.



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

  from IArena.games.VectorWordle import VectorWordlePosition
  from IArena.games.VectorWordle import VectorWordleMovement
  from IArena.games.VectorWordle import VectorWordleRules


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
  movement = VectorWordleMovement(guess=[0, 1, 2])

.. warning::

  Depending on the rules, the guess could be invalid if has repeated values (the same number more than once).


========
Position
========

A position is represented by a list of movements (guesses) and a list of feedback.

--------
Feedback
--------

The feedback of each guess comes in 3 different lists:

- ``last_positive_feedback() -> List[int]``: List of indexes for each value in last guess in correct position.
- ``last_misplaced_feedback() -> List[int]``: List of indexes for each value in the last guess that are in the code but misplaced.
- ``last_negative_feedback() -> List[int]``: List of indexes for each value in last guess that are not in the code.

These values can be acquired from the general feedback list:

- ``positive_feedback() -> List[List[int]]``: List with all the positive feedbacks so far.
- ``misplaced_feedback() -> List[List[int]]``: List with all the misplaced feedbacks so far.
- ``negative_feedback() -> List[List[int]]``: List with all the negative feedbacks so far.


.. code-block:: python

  # position : VectorWordlePosition
  guesses = position.guesses()

  positive_feedback = position.positive_feedback()
  misplaced_feedback = position.misplaced_feedback()
  negative_feedback = position.negative_feedback()

  guesses[-1]  # Last guess
  guesses[-1][0]  # First value of the last guess

  # This is a vector of positions [0,M) representing which indexes are in correct position
  correct_positions = positive_feedback[-1]

  if 0 in correct_positions:
    # The first value of the last guess is correct
  elif 0 in misplaced_feedback[-1]:
    # The first value of the last guess is in the code but misplaced
  elif 0 in negative_feedback[-1]:
    # The first value of the last guess is not in the code


Example
^^^^^^^

For example, let's imagine an scenario where ``N=4``, ``M=6``, the secret code is ``[1, 3, 5, 4]``.
If the player makes the guess ``[1,2,3,4]``, the feedback will be:

- ``last_positive_feedback() -> [0, 3]``: The first and forth values (1 and 4) are correct.
- ``last_misplaced_feedback() -> [2]``: The third value (3) is in the code but misplaced.
- ``last_negative_feedback() -> [1]``: The second value (2) is not in the code.



-------
Methods
-------

- ``guesses() -> List[VectorWordleMovement]``: List of guesses made so far.
- ``last_guess() -> VectorWordleMovement``: Last guess made.
- ``positive_feedback() -> List[List[int]]``: List with all the positive feedbacks so far.
- ``misplaced_feedback() -> List[List[int]]``: List with all the misplaced feedbacks so far.
- ``negative_feedback() -> List[List[int]]``: List with all the negative feedbacks so far.
- ``last_positive_feedback() -> List[int]``: List of indexes for each value in last guess in correct position.
- ``last_misplaced_feedback() -> List[int]``: List of indexes for each value in the last guess that are in the code but misplaced.
- ``last_negative_feedback() -> List[int]``: List of indexes for each value in last guess that are not in the code.
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
    rules = VectorWordleRules(
        code_size=4,
        number_values=6,
        secret=[0, 1, 2, 3],
        allow_repetition=False
    )
