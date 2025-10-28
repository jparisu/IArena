.. _letterwordle_docs:

######
LetterWordle
######

.. figure:: /resources/images/wordle.png
    :scale: 30%

This game is a version of the New York Times game LetterWordle, as 1 player guess game: `this link <https://www.nytimes.com/games/Letterwordle/index.html>`.
The objective of the game is to guess the *secret code*, this is a sequence of *N* letters chosen from *M* letters available ``['a', M)``.
Each turn the player has to guess the code.
After each guess, the game will tell the player which of the guesses appears in the code but are not correctly positioned, and which ones are correctly positioned.
The goal is to guess the code in the fewest number of turns.

Some changes have been made to the original game:

- There are 2 versions: **with repetitions** (same letter could appear more than once in the code) and **without repetitions**.

The online version of the game can be found at `this link <https://www.nytimes.com/games/Letterwordle/index.htmll>`_.
Be aware that this version differ from the game implemented here as explained before.


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

  from IArena.games.LetterWordle import LetterWordlePosition
  from IArena.games.LetterWordle import LetterWordleMovement
  from IArena.games.LetterWordle import LetterWordleRules


========
Movement
========

A movement has a *guess* in the format of ``List[str]``.
It must have ``N`` letters in the range ``['a',Mth letter)``.

- ``guess``
  - ``List[str]``
  - ``len == N``
  - ``ord('a') <= l[i] < ord('a') + M``
  - Guess of the secret code


.. code-block:: python

  # A guess in a game with N=3 and M>2
  movement = LetterWordleMovement(guess=['a', 'b', 'c'])

.. warning::

  Depending on the rules, the guess could be invalid if has repeated values (the same letter more than once).


========
Position
========

A position is represented by a list of movements (guesses) and a list of feedback.

--------
Feedback
--------

A ``LetterWordleFeedback`` is an enumeration with the following values:

- ``Wrong``: 0
- ``Misplaced``: 1
- ``Correct``: 2

The feedback of a guess is a list of ``LetterWordleFeedback`` indicating for each of the values in the guess,
if it is correctly placed (``2``),
if it is in the secret code, but misplaced (``1``),
or whether it is not present in the secret code (``0``).

.. code-block:: python

  # position : LetterWordlePosition
  guesses = position.guesses()
  feedback = position.feedback()

  guesses[-1]  # Last guess
  guesses[-1][0]  # First position of the last guess

  feedback[-1]  # Feedback of the last guess
  c = feedback[-1][0]  # Feedback of the first position of the last guess

  if c == LetterWordlePosition.LetterWordleFeedback.Correct:
    # The first value of the last guess is correct
  elif c == LetterWordlePosition.LetterWordleFeedback.Misplaced:
    # The first value of the last guess is in the code but in other position
  else:
    # The third value of the last guess is wrong


-------
Methods
-------

- ``guesses() -> List[LetterWordleMovement]``: List of guesses made so far.
- ``feedback() -> List[List[LetterWordleFeedback]]``: List of feedback lists made so far.
- ``last_guess() -> LetterWordleMovement``: Last guess made.
- ``last_feedback() -> List[LetterWordleFeedback]``: Feedback of the last guess.
- ``code_size() -> int``: Number of values in the secret code (N).
- ``letters() -> int``: Number of different letters available (M). If no repetitions allowed, M >= N.
- ``allow_repetition() -> bool``: Whether the secret code can have repeated values.
- ``possible_letters() -> List[str]``: List of letters that could be in the secret code. This is the list of letters from 'a' to the M-th letter.

=====
Rules
=====

This object defines the rules of the game, including the secret code.
When constructed, it sets the secret code, the number of values in the code (N), and the number of different values available (M), and whether repetitions are allowed.



-------
Methods
-------

- ``code_size() -> int``: Number of values in the secret code (N).
- ``letters() -> int``: Number of different values available (M). If no repetitions allowed, M >= N.
- ``allow_repetition() -> bool``: Whether the secret code can have repeated values.
- ``possible_letters() -> List[str]``: List of letters that could be in the secret code. This is the list of letters from 'a' to the M-th letter.


-----------
Constructor
-----------

Arguments for constructor are:

- ``code_size: int``: N
- ``letters: int``: M
- ``secret: List[int]``: List of N values between ``[0,M)`` representing the secret code.
- ``allow_repetition: bool``: Whether the secret code can have repeated values.


1. Using a secret code already defined.

  .. code-block:: python

    # Secret code with N=4 and M=6
    rules = LetterWordleRules(
        code_size=4,
        letters=6,
        secret=['a', 'b', 'c', 'd'],
        allow_repetition=False
    )



=========
ord & chr
=========

There are 2 functions that could be useful when working with this game: ``ord`` and ``chr``.

- ``ord(c: str) -> int``: Given a character ``c``, it returns its ASCII code.
- ``chr(i: int) -> str``: Given an integer ``i``, it returns the character corresponding to its ASCII code.

For example, to get the M-th letter from 'a', you can use:

.. code-block:: python

  M = 5
  mth_letter = chr(ord('a') + M - 1)  # 'e'
