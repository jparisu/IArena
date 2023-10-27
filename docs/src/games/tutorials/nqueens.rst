.. _nqueens_tutorial:

#######
NQueens
#######

.. figure:: /resources/images/nqueens.svg
    :scale: 80%

This game is the classical N-Queens puzzle.
The objective of the game is to place ``N`` queens on a ``N x N`` chessboard so that no two queens attack each other.
The attack of the queens follows the rules of chess: a queen can attack horizontally, vertically and diagonally.

The game has a chessboard (square grid) of ``N x N`` squares.
Each movement indicates the place of a new queen in the chessboard.
After ``N`` movements, the optimal score is reached when no queens attack each other.

====
Goal
====

After placing ``N`` queens on a ``N x N`` chessboard, the queens must attack as less other queens as possible.

-----
Score
-----

``+1`` for each queen in the range of attack of other queen.
*This will always give even scores.*


======
Import
======

.. code-block:: python

  import IArena.games.NQueens.NQueensPosition as NQueensPosition
  import IArena.games.NQueens.NQueensMovement as NQueensMovement
  import IArena.games.NQueens.NQueensRules as NQueensRules


========
Movement
========

A movement is represented by a tuple ``new_position`` of 2 ``int``:

- ``new_position``
  - ``tuple(int, int)``
    - ``int``
    - ``0 <= tower_source < N``
    - Number of row to place the next queen.
  - ``tuple(int, int)``
    - ``int``
    - ``0 <= tower_source < N``
    - Number of column to place the next queen.


.. code-block:: python

    movement = NQueensMovement(new_position=[0, 0])


========
Position
========

A position is represented by an ``int`` describing the size of the board, and a ``list`` of movements.
Each movement represents the position of a queen in the board.

.. code-block:: python

  # position : NQueensPosition
  position.n                  # The size of the board is n x n
  len(position.positions)     # Number of queens already in the board
  position.positions[0][0]    # Row of the first queen
  position.positions[-1][1]   # Column of the last queen


=====
Rules
=====

This games has every methods of :ref:`IRules <infrastructure_rules>`.

Remember that using ``score`` method can give the current result of the game:

.. code-block:: python

  # rules     : NQueensRules
  # position  : NQueensPosition
  rules.score(position)   # Returns how many queens are attacking each other


-----------
Constructor
-----------

Can receive an argument ``n : int`` that represents the size of the board.


.. code-block:: python

  # Initial board of 8x8
  rules = nqueensRules()

  # Initial board of 5x5
  rules = nqueensRules(n=5)
