.. _numberguess_docs:

###########
NumberGuess
###########

This game is simple number guesser, as 1 player guess game.
The objective of the game is to guess the *secret number*, this is a number chosen from *M* numbers available ``[0,M)``.
Each turn the player has to guess the number.
After each guess, the game check if the number is correct, and if not, it calls the player again.
The goal is to guess the code in the fewest number of turns.


====
Goal
====

Guess the correct *number* in the fewest number of turns.

-----
Score
-----

The score is ``-T`` where ``T`` is the number of turns needed to guess the number.
The highest the score, the better.


======
Import
======

.. code-block:: python

  from IArena.games.NumberGuess import NumberGuessPosition
  from IArena.games.NumberGuess import NumberGuessMovement
  from IArena.games.NumberGuess import NumberGuessRules


========
Movement
========

A movement has a *guess* in the format of ``int``.
It must have an integer in the range ``[0,M)``.

- ``guess``
  - ``int``
  - ``0 <= l[i] < M``
  - Guess of the number


.. code-block:: python

  # A guess with number 1
  movement = NumberGuessMovement(guess=1)


========
Position
========

A position is represented by the list of movements (guesses) so far.

-------
Methods
-------

- ``guesses() -> List[NumberGuessMovement]``: List of guesses made so far.
- ``last_guess() -> NumberGuessMovement``: Last guess made.
- ``number_values() -> int``: Number of different values available (M). If no repetitions allowed, M >= N.


.. code-block:: python

  # position : NumberGuessPosition

  guesses = position.guesses()  # List of guesses so far (as NumberGuessMovement)

  last_guess = position.last_guess()  # Last guess made (as NumberGuessMovement)
  last_guess_number = last_guess.guess  # The number guessed (as int)

  M = position.number_values()  # Number of different values available: [0,M)



=====
Rules
=====

This object defines the rules of the game, including the secret number.
When constructed, it sets the secret number, and the number of different values available (M).


-------
Methods
-------

- ``number_values() -> int``: Number of different values available (M). If no repetitions allowed, M >= N.


-----------
Constructor
-----------

Arguments for constructor are:

- ``number_values: int``: M
- ``secret: int``: Integer between ``[0,M)`` representing the number.


1. Using a number already defined.

  .. code-block:: python

    # Secret code with  M=6
    rules = NumberGuessRules(
        number_values=6,
        secret=3,
    )



.. _numberguess_playable_player:

===============
Playable Player
===============

This game implements a ``PlayablePlayer`` interface that allows to play manually with a simple text interface.

In order to test it in a game, you can do the following:

.. code-block:: python

  from IArena.games.NumberGuess import NumberGuessRules, NumberGuessPlayablePlayer
  from IArena.arena.GenericGame import GenericGame

  rules = NumberGuessRules(number_values=6, secret=3)

  player = NumberGuessPlayablePlayer(name="Human")

  game = GenericGame(rules=rules, players=[player])

  score = game.play()

  print(score.pretty_print())
