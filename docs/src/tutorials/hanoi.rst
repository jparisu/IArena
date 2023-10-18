.. _hanoi_tutorial:

#####
Hanoi
#####

.. figure:: /resources/images/hanoi.png

This game is the classical Tower of Hanoi puzzle.
The objective of the game is to move the entire stack of disks from the leftmost to the rightmost rod.
Only one disk may be moved at a time from the top of one tower to the top of another,
and it is not possible to place a bigger disk on top of a smaller disk.

The game has three rods and a number of disks ``N`` that can vary from one game to another.
The game starts with ``N`` disks in ascending order of size on the leftmost rod.

====
Goal
====

The final position of the game is when all the disks are in the rightmost rod (tower index ``2``).

-----
Score
-----

The score of the game is the number of movements to reach the final position.


======
Import
======

.. code-block:: python

  import IArena.games.Hanoi.HanoiPosition as HanoiPosition
  import IArena.games.Hanoi.HanoiMovement as HanoiMovement
  import IArena.games.Hanoi.HanoiRules as HanoiRules


========
Movement
========

A movement is represented by 2 ``int``: ``tower_source`` and ``tower_target``.

- ``tower_source``
  - ``int``
  - ``0 <= tower_source < 3``
  - Indicates the index of the tower from which the top disk will be removed.

- ``tower_target``
  - ``int``
  - ``0 <= tower_target < 3`` and ``tower_source != tower_target``
  - Indicates the index of the tower where the disk removed will be placed.


.. code-block:: python

    movement = HanoiMovement(tower_source=0, tower_target=1)


========
Position
========

A position is represented by a ``List[List[int]]`` and a cost in ``int`` format.
Each element of the list represents a tower.
Each tower has a list of ``int`` that represents the disks in the tower.
The disks go from ``0`` to ``N-1`` in ascending order being ``0`` the highest disk.


.. code-block:: python

  # position : HanoiPosition
  position.towers[0][0]   # lowest disk of the leftmost tower
  position.towers[2][-1]  # highest disk of the rightmost tower
  position.cost           # number of movements to reach this position


=====
Rules
=====

This games has every methods of :ref:`IRules <infrastructure_rules>`.


Position

It has a *static* method ``generate_initial_position`` that returns the initial position of the game giving and ``int`` for number of disks.

.. code-block:: python

  HanoiRules.generate_initial_position(n=4) # initial position with 4 disks


-----------
Constructor
-----------

Can receive an argument ``initial_towers : List[List[int]]`` that represents the initial state of the disks in the initial position.


.. code-block:: python

  # Initial position with 4 disks
  rules = HanoiRules()

  # Initial position with 5 disks
  rules = HanoiRules(n=5)
