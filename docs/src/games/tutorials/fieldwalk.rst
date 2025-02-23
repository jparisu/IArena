.. _fieldwalk_tutorial:

#########
FieldWalk
#########

.. figure:: /resources/images/fieldwalk.png
    :scale: 60%

This game represents a search in a square graph of the shortest path.
In a square of ``NxM``, each cell has a cost that represents the cost of passing through that cell.
From each cell, the player can go to one of the 4 adjacent cells (up, down, left, right).
The objective is to reach the bottom-right cell ``[N-1,M-1]`` from the top-left cell ``[0,0]`` with the minimum cost.

====
Goal
====

Starting at ``[0,0]``, the goal is to reach ``[N-1,M-1]`` with the minimum cost.

-----
Score
-----

The score of the game is the sum of the values of the squares that the player has passed through (initial square does not count).


======
Import
======

.. code-block:: python

  from IArena.games.FieldWalk import FieldWalkPosition
  from IArena.games.FieldWalk import FieldWalkMovement
  from IArena.games.FieldWalk import FieldWalkRules


========
Movement
========

A movement is represented an ``int``: ``direction``.

- ``direction``
  - ``int``
  - ``0 <= direction <= 3``
  - Indicates the direction of the movement
  - Some movements are not possible if they go out of the board

---------
Direction
---------

Enumeration of the possible directions:

- ``Up``
  - ``0``
- ``Down``
  - ``1``
- ``Left``
  - ``2``
- ``Right``
  - ``3``


.. code-block:: python

    # To move up
    movement = FieldWalkMovement.up()
    # or
    movement = FieldWalkMovement(
      direction=FieldWalkMovement.Direction.Up)



========
Position
========

A position is represented by 3 ``int``.
One indicates the x axis, other the y axis and the last one the cost to arrive to the current position.


.. code-block:: python

  # position : FieldWalkPosition
  position.x     # X axis [0, N-1]
  position.y     # Y axis [0, M-1]
  position.cost  # Cost to arrive to this position


=====
Rules
=====


-----------
Constructor
-----------

Can receive the map, or let it be created randomly.

.. code-block:: python

  # Initiate with a map of 2x2 with cost 1
  rules = FieldWalkRules(initial_map=FieldWalkMap([[1,1],[1,1]]))

  # Initial position board 5x4 with random cost
  rules = FieldWalkRules(rows=5, cols=4)

  # Replicable initial position board 5x4 with random cost
  rules = FieldWalkRules(rows=5, cols=4, seed=0)


---
Map
---

This game counts with a class ``FieldWalkMap`` that represents the grid of the game.
This is created from a ``List[List[int]]``.
The method ``get_matrix()`` returns the list of lists with all the values.

.. code-block:: python

  # get the FieldWalkMap
  fw_map = rules.get_map()

  # Get the size
  N, M = len(fw_map)
  # or
  N, M = fw_map.goal()

  # Get the matrix of the map
  fw_map.get_matrix().get_matrix()

  # Get the value of the final position
  value = fw_map.get_matrix()[N-1][M-1]
  # or
  value = fw_map[N-1,M-1]
