.. _mastermind_tutorial:

##########
Mastermind
##########

.. figure:: /resources/images/mastermind.png

This game is the classical Mastermind game.
The objective of the game is to guess the *secret code*, this is a sequence of *N* numbers (color pegs) chosen from *M* numbers available ``[0,M)``.
Each turn the player has to guess the code.
After each guess, the game will tell the player which of the guesses appears in the code but are not correctly positioned, and which ones are correctly positioned.
The goal is to guess the code in the fewest number of turns.

Some changes have been made to the original game:

- There is only a one player game (guesser) while the other player (codemaker) is the game itself.
- Instead of colors we use numbers.
- The clues of each guess is not only the number of appearance and correctness, but are linked with a direct position in the guess.
- Numbers could be repeated in the secret code.

====
Goal
====

Guess the correct *secret code* in the fewest number of turns.

-----
Score
-----

The number of turns needed to guess the secret code.


======
Import
======

.. code-block:: python

  import IArena.games.Mastermind.MastermindPosition as MastermindPosition
  import IArena.games.Mastermind.MastermindMovement as MastermindMovement
  import IArena.games.Mastermind.MastermindRules as MastermindRules


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


========
Position
========

A position is represented by a list of movements (guesses) and a list of correctness.

-----------
Correctness
-----------

A ``MastermindCorrectness`` is an enumeration with the following values:

- ``Wrong``: 0
- ``Misplaced``: 1
- ``Correct``: 2

The correctness of a guess is a list of ``MastermindCorrectness`` indicating for each of the values in the guess,
if it is correctly placed (``2``),
if it is in the secret code, but misplaced (``1``),
or whether it is not present in the secret code (``0``).

.. code-block:: python

  # position : MastermindPosition
  guesses = position.guesses
  correctness = position.correctness

  guesses[-1][0]  # First position of the last guess

  if correctness[-1][0] == MastermindPosition.MastermindCorrectness.Correct:
    # The first value of the last guess is correct
  elif correctness[-1][1] == MastermindPosition.MastermindCorrectness.Misplaced:
    # The second value of the last guess is in the code but in other position
  else:
    # The third value of the last guess is wrong


=====
Rules
=====

This games has every methods of :ref:`IRules <infrastructure_rules>`.

It counts with 2 methods to get the minimum and maximum number of coins that can be taken:

- ``rules.get_size_code() -> int``
- ``rules.get_number_colors() -> int``


-----------
Constructor
-----------

There are 2 ways to construct the rules:

#. Using a secret code already defined.

  .. code-block:: python

    # Secret code with N=4 and M=6
    rules = MastermindRules(secret=[0, 1, 2, 3], m=6)

    # Secret code with N=8 and M=8
    rules = MastermindRules(secret=[0, 0, 0, 0, 0, 0, 0, 7], m=8)


#. Setting arguments ``n: int`` and ``m: int`` in order to generate a random secret code.
   Using argument ``seed: int`` the random generation can be reproduced.

  .. code-block:: python

    # Random secret code with N=4 and M=6
    rules = MastermindRules()

    # Random secret code with N=8 and M=8 reproducible
    rules = MastermindRules(n=8, m=8, seed=0)
