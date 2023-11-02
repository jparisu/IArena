.. _slicing_tutorial:

##############
Slicing Puzzle
##############

.. figure:: /resources/images/slicing.jpg
    :scale: 10%

This game is the classical Slicing puzzle.
In a board of ``N x N`` squares, where every square has a number between ``[0, N-2]``, there is one of the squares that is *empty* (``-1``).
The objective is to sort all the squares in the board in the lowest number of movements.
A movement is moving one of the squares next to the empty square to the empty square, becoming its position as the new empty square.

====
Goal
====

Sort the board in the lowest number of movements.
A board is considered solved when all the squares are sorted in ascending order, sorting first rows and then columns.
In the solved board the empty square is in the bottom right corner.

-----
Score
-----

The number of movements needed to solve the board.


======
Import
======

.. code-block:: python

  from IArena.games.SlicingPuzzle import SlicingPuzzlePosition
  from IArena.games.SlicingPuzzle import SlicingPuzzleMovement
  from IArena.games.SlicingPuzzle import SlicingPuzzleRules


========
Movement
========

A movement is represented by an enumeration with 4 values:

- ``Up``
  - ``0``
  - Move the square below the empty one to the empty square.
  - Move the empty square down.
- ``Down``
  - ``1``
  - Move the square above the empty one to the empty square.
  - Move the empty square up.
- ``Left``
  - ``2``
  - Move the square to the right of the empty one to the empty square.
  - Move the empty square to the right.
- ``Right``
  - ``3``
  - Move the square to the left of the empty one to the empty square.
  - Move the empty square to the left.


.. code-block:: python

    # Move Up
    movement = SlicingPuzzleMovement.Values.Up

    # Move Left
    movement = SlicingPuzzleMovement.Values.Left


========
Position
========

The position is represented by a ``List[List[int]]``.
The size of the board is ``n x n``.
The value of each square is between ``[0, n-2]``.
The empty square is represented by ``-1``.

It counts with the following methods:

- ``empty_space``
  - Retrieve the position of the empty square.
  - Returns a tuple ``(row, column)``.
- ``len``
  - Get the size of the board
- ``cost``
  - Get the number of movements made so far

.. code-block:: python

  # position : SlicingPuzzlePosition
  position.n                  # Size of the board: n x n
  len(position.positions)     # Size of the board: n x n

  x, y = positions.empty_space()  # Row and Col of the empty square

  position.squares            # The board
  position.squares[0][0]      # The number in the upper left corner
  position.positions[-1][-1]  # The number in the bottom right corner

  position.cost()             # Number of movements so far


=====
Rules
=====

This games has every methods of :ref:`IRules <infrastructure_rules>`.


-----------
Constructor
-----------

Can receive the initial position of the numbers,
or the size of the board (``n``) and it will generate a random position.


.. code-block:: python

  # Random initial board of 3x3
  rules = SlicingPuzzleRulesRules()

  # Random initial board of 4x4 reproducible
  rules = SlicingPuzzleRulesRules(n=4, seed=0)

  # Initial board of 3x3 predefined
  rules = SlicingPuzzleRulesRules(initial_position=[[1, 2, 3], [4, 5, 6], [-1, 7, 8]])
