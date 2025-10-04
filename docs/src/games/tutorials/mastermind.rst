.. _mastermind_docs:

##########
Mastermind
##########

.. figure:: /resources/images/mastermind.png
    :scale: 8%

This game is the classical Mastermind game as 1 player version.
The objective of the game is to guess the *secret code*, this is a sequence of *N* numbers (color pegs) chosen from *M* numbers available ``[0,M)``.
Each turn the player has to guess the code.
After each guess, the game will tell the player which of the guesses appears in the code but are not correctly positioned, and which ones are correctly positioned.
The goal is to guess the code in the fewest number of turns.

Some changes have been made to the original game:

- There is only one player (guesser) while the other player (password-maker) is not considered a player.
- Instead of colors we use numbers.
- There are 2 versions: **with repetitions** (same number could appear more than once in the code) and **without repetitions**.

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

  from IArena.games.Mastermind import MastermindPosition
  from IArena.games.Mastermind import MastermindMovement
  from IArena.games.Mastermind import MastermindRules


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
  movement = MastermindMovement(guess=[0, 1, 2])

.. warning::

  Depending on the rules, the guess could be invalid if has repeated values (the same number more than once).


========
Position
========

A position is represented by a list of movements (guesses) and a list of feedback.

--------
Feedback
--------

A ``MastermindFeedback`` is an object that contains 2 integer values:

- ``correct``: the number of values in the guess that are correctly placed.
- ``misplaced``: the number of values in the guess that are in the secret code but misplaced.


.. code-block:: python

  # position : MastermindPosition
  guesses = position.guesses()
  feedback = position.feedback()

  guesses[-1]  # Last guess
  guesses[-1][0]  # First position of the last guess

  correct = feedback[-1].correct  # Number of correct values in the last guess
  misplaced = feedback[-1].misplaced  # Number of misplaced values in the last guess


-------
Methods
-------

- ``guesses() -> List[MastermindMovement]``: List of guesses made so far.
- ``feedback() -> List[List[MastermindFeedback]]``: List of feedback lists made so far.
- ``last_guess() -> MastermindMovement``: Last guess made.
- ``last_feedback() -> List[MastermindFeedback]``: Feedback of the last guess.
- ``code_size() -> int``: Number of values in the secret code (N).
- ``number_values() -> int``: Number of different values available (M). If no repetitions allowed, M >= N.


=====
Rules
=====

This object defines the rules of the game, including the secret code.
When constructed, it sets the secret code, the number of values in the code (N), and the number of different values available (M), and whether repetitions are allowed.



-------
Methods
-------

- ``size_code() -> int``: Number of values in the secret code (N).
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
    rules = MastermindRules(
        code_size=4,
        number_values=6,
        secret=[0, 1, 2, 3],
        allow_repetition=False
    )



.. _mastermind_playable_player:

===============
Playable Player
===============

This game implements a ``PlayablePlayer`` interface that allows to play manually with a simple text interface.

In order to test it in a game, you can do the following:

.. code-block:: python

  from IArena.games.Mastermind import MastermindPlayablePlayer
  from IArena.arena.GenericGame import GenericGame

  rules = MastermindRules(code_size=4, number_values=6, secret=[0, 1, 2, 3], allow_repetition=False)

  player = MastermindPlayablePlayer(name="Human")

  game = GenericGame(rules=rules, players=[player])

  score = game.play()

  print(score.pretty_print())
