.. _coins_tutorial:

#####
Coins
#####

.. figure:: /resources/images/coins.svg

This game is a classical 2 players game called *Roman Coins*.
By turns, each player takes between ``A`` and ``B`` coins from a pile of ``N`` coins.
The player that can no longer take a coins loses.

This is a **0 sum** game with perfect information.

====
Goal
====

The goal of this game is to be the last player to take a coin.

-----
Score
-----

- The player that takes the last coin:
  - ``0``
- The player that cannot take a coin:
  - ``1``

======
Import
======

.. code-block:: python

  import IArena.games.Coins.CoinsPosition as CoinsPosition
  import IArena.games.Coins.CoinsMovement as CoinsMovement
  import IArena.games.Coins.CoinsRules as CoinsRules


========
Movement
========

A movement is represented by an ``int`` representing the number of coins to take:

- ``n``
  - ``int``
  - ``A <= tower_source < min(B, number of coins remaining)``
  - Number of coins to remove


.. code-block:: python

    movement = CoinsMovement(n=2) # Remove 2 coins from the stack


========
Position
========

A position is represented by an ``int`` describing the size of the remaining stack.

.. code-block:: python

  # position : CoinsPosition
  len(position)      # Size of the stack
  position.n         # Same as len


=====
Rules
=====

This games has every methods of :ref:`IRules <infrastructure_rules>`.

It counts with 2 methods to get the minimum and maximum number of coins that can be taken:

- ``rules.min_play() -> int``
- ``rules.max_play() -> int``


-----------
Constructor
-----------

Can receive 3 arguments:

- ``initial_position``
  - ``int``
  - ``0 <= initial_position``
  - Initial size of the stack
  - Default: ``15``
- ``min_play``
  - ``int``
  - ``1 <= min_play``
  - Minimum number of coins that can be taken in a turn
  - Default: ``1``
- ``max_play``
  - ``int``
  - ``min_play <= max_play``
  - Maximum number of coins that can be taken in a turn
  - Default: ``3``


.. code-block:: python

  # Stack of 15 coins with min_play=1 and max_play=3
  rules = coinsRules()

  # Stack of 20 coins with min_play=2 and max_play=5
  rules = coinsRules(
    initial_position=20,
    min_play=2,
    max_play=5)
