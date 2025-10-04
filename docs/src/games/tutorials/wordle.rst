.. _mastermind_docs:

######
Wordle
######

.. figure:: /resources/images/wordle.png
    :scale: 30%

This game is the classical Wordle game as 1 player version.
The objective of the game is to guess the *secret code*, this is a sequence of *N* numbers (color pegs) chosen from *M* numbers available ``[0,M)``.
Each turn the player has to guess the code.
After each guess, the game will tell the player which of the guesses appears in the code but are not correctly positioned, and which ones are correctly positioned.
The goal is to guess the code in the fewest number of turns.

Some changes have been made to the original game:

- There is only one player (guesser) while the other player (password-maker) is not considered a player.
- Instead of colors we use numbers.
- The clues of each guess is not only the number of appearance and correctness, but are linked with a direct position in the guess.
- There are 2 versions: **with repetitions** (same number could appear more than once in the code) and **without repetitions**.

An online version of the game can be found at `this link <https://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/guess.html>`_.
Be aware that this version does not give clues linked to the position of the guess, so the game implemented here is slightly different.


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

  from IArena.games.Wordle import WordlePosition
  from IArena.games.Wordle import WordleMovement
  from IArena.games.Wordle import WordleRules


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
  movement = WordleMovement(guess=[0, 1, 2])

.. warning::

  Depending on the rules, the guess could be invalid if has repeated values (the same number more than once).


========
Position
========

A position is represented by a list of movements (guesses) and a list of correctness.

-----------
Correctness
-----------

A ``WordleCorrectness`` is an enumeration with the following values:

- ``Wrong``: 0
- ``Misplaced``: 1
- ``Correct``: 2

The correctness of a guess is a list of ``WordleCorrectness`` indicating for each of the values in the guess,
if it is correctly placed (``2``),
if it is in the secret code, but misplaced (``1``),
or whether it is not present in the secret code (``0``).

.. code-block:: python

  # position : WordlePosition
  guesses = position.guesses()
  correctness = position.correctness()

  guesses[-1]  # Last guess
  guesses[-1][0]  # First position of the last guess

  correctness[-1]  # Correctness of the last guess
  c = correctness[-1][0]  # Correctness of the first position of the last guess

  if c == WordlePosition.WordleCorrectness.Correct:
    # The first value of the last guess is correct
  elif c == WordlePosition.WordleCorrectness.Misplaced:
    # The first value of the last guess is in the code but in other position
  else:
    # The third value of the last guess is wrong


-------
Methods
-------

- ``guesses() -> List[WordleMovement]``: List of guesses made so far.
- ``correctness() -> List[List[WordleCorrectness]]``: List of correctness lists made so far.
- ``last_guess() -> WordleMovement``: Last guess made.
- ``last_correctness() -> List[WordleCorrectness]``: Correctness of the last guess.

=====
Rules
=====

This object defines the rules of the game, including the secret code.
When constructed, it sets the secret code, the number of values in the code (N), and the number of different values available (M), and whether repetitions are allowed.



-------
Methods
-------

- ``get_size_code() -> int``: Number of values in the secret code (N).
- ``get_number_colors() -> int``: Number of different values available (M). If no repetitions allowed, M >= N.
- ``allow_repetition() -> bool``: Whether the secret code can have repeated values.


-----------
Constructor
-----------

Arguments for constructor are:

- ``code_size: int``: N
- ``number_colors: int``: M
- ``secret: List[int]``: List of N values between ``[0,M)`` representing the secret code.
- ``allow_repetitions: bool``: Whether the secret code can have repeated values.


1. Using a secret code already defined.

  .. code-block:: python

    # Secret code with N=4 and M=6
    rules = WordleRules(
        code_size=4,
        number_colors=6,
        secret=[0, 1, 2, 3],
        allow_repetitions=False
    )



.. _mastermind_playable_player:

===============
Playable Player
===============

This game implements a ``PlayablePlayer`` interface that allows to play manually with a simple text interface.

In order to test it in a game, you can do the following:

.. code-block:: python

  from IArena.games.Wordle import WordlePlayablePlayer
  from IArena.arena.GenericGame import GenericGame

  rules = WordleRules(code_size=4, number_colors=6, secret=[0, 1, 2, 3], allow_repetitions=False)

  player = WordlePlayablePlayer(name="Human")

  game = GenericGame(rules=rules, players=[player])

  score = game.play()

  print(score.pretty_print())
