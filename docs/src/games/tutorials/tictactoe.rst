.. _tictactoe_tutorial:

###########
Tic-Tac-Toe
###########

.. figure:: /resources/images/tictactoe.png
    :scale: 40%

This game is a classical 2 players game called *Tic-Tac-Toe* or 3 in a row.
In a board of 3x3 each player plays each turn by putting a piece of his color in an empty cell.
The player that aligns 3 pieces of his color horizontally, vertically or diagonally wins.
If the board is full and no player has aligned 3 pieces, the game is a draw.

This is a **0 sum** game with perfect information.

====
Goal
====

The goal of this game is to

-----
Score
-----

- If there is a winner
  - Winner gets ``0``
  - Loser gets ``3``
- If the game is a draw
  - Both get ``1``

======
Import
======

.. code-block:: python

  from IArena.games.TicTacToe import TicTacToePosition
  from IArena.games.TicTacToe import TicTacToeMovement
  from IArena.games.TicTacToe import TicTacToeRules


========
Movement
========

A movement is represented by 2 ``int`` representing the number of the row and the number of sticks:

- ``row``
  - ``int``
  - ``0 <= row < 3``
  - Index of the row to place the piece
- ``column``
  - ``int``
  - ``0 <= column < 3``
  - Index of the column to place the piece

.. code-block:: python

    movement = TicTacToeMovement(
      row=1,
      column=1)
    # Place in the middle of the board


========
Position
========

A position is represented by a ``list`` of ``list`` of ``int`` describing the board.
Each position is represented by an integer, ``0`` for empty, ``1`` for player 1 and ``2`` for player 2.

.. code-block:: python

  # position : TicTacToePosition
  x = position[0][0]        # Player in the top left corner
  if x == 0:
    # Empty cell
  elif x == 1:
    # Player 1
  elif x == 2:
    # Player 2

  board = position.board
  x = board[0][0]        # Player in the top left corner


=====
Rules
=====



-----------
Constructor
-----------

Can receive 1 argument:

- ``initial_position``
  - ``List[List[int]]``
  - The initial position of the game
  - Default: ``None`` empty board


.. code-block:: python

  # Start empty board game
  rules = TicTacToeRules()

  # Start game with first player played in the center
  rules = TicTacToeRules(
    original_lines=[[0,0,0],[0,1,0],[0,0,0]])
