.. _games:

#####
Games
#####

In this module there is explained the structure of a **Game** or **Rule**.
It also enumerates the different games supported so far by the library.

==========
Interfaces
==========

There are 3 main interfaces that represent a **game**.
The *IGameRules* holds the logic of the game.
The *IPosition* represents a position or state of the game regarding a specific set of rules.
The *IMovement* represents a movement of the game that goes from one position to another.

.. _rules:

------
IRules
------

Represent the rules of a game implementing the following methods:

.. list-table::

  * - **Method**
    - **Description**
    - **Arguments type**
    - **Return type**
    - **Must be implemented for each game**

  * - ``n_players()``.
    - The number of players
    - ``-``
    - ``int``
    - *Yes*.

  * - ``first_position()``.
    - The initial position.
    - ``-``
    - ``IPosition``
    - *Yes*.

  * - ``next_position()``.
    - The next position giving a position and a move.
    - ``movement: IMovement, position: IPosition``
    - ``IPosition``
    - *Yes*.

  * - ``possible_movements()``.
    - The possible moves giving a position.
    - ``IPosition``
    - ``List[IMovements]``
    - *Yes*.

  * - ``finished()``.
    - Whether a position is terminal.
    - ``IPosition``
    - ``bool``
    - *Yes*.

  * - ``score()``.
    - The score of a terminal position.
    - ``IPosition``
    - ``ScoreBoard``
    - *Yes*.

  * - ``is_movement_possible()``.
    - Whether a move is possible giving a position.
    - ``movement: IMovement, position: IPosition``
    - ``bool``
    - *No*.



.. _movement:

---------
IMovement
---------

Represent a movement of a game.
It does not have general methods, as each movement depends on the rules of the specific game.


.. _position:

---------
IPosition
---------

Represent a position of a game.
This means, a state, a position of a board, a position in a map, etc.
Some variables referring to the position may be stored in the rules object that has generated this position.

.. list-table::

  * - **Method**
    - **Description**
    - **Arguments type**
    - **Return type**
    - **Must be implemented for each game**

  * - ``next_player()``.
    - The next player to play.
    - ``-``
    - ``PlayerIndex``
    - *Yes*.

  * - ``get_rules()``.
    - Rules that has generated this position.
    - ``-``
    - ``IGameRules``
    - *No*.

==========
ScoreBoard
==========

The Score measured in a ``float`` variable indicates for each player how good the final game went.
After finishing any game, you get a ``ScoreBoard`` that holds the score for each player.

.. note::

    Always remember that the lowest score is the best one.


.. _games_available:

===============
Games available
===============

This is a list of all the games supported and its characteristics:

.. list-table:: Games

   * - **Game name**
     - **Folder**
     - **Tutorial**
     - **Short description**
     - **Number of players**
     - **Deterministic / Random**
     - **Perfect information / Hidden information**
     - **Details**

   * - **Hanoi**
     - ``IArena.games.Hanoi``
     - :ref:`hanoi_tutorial`
     - The classic Hanoi's Tower game.
     - 1
     - Deterministic
     - Perfect information
     -

   * - **SlicingPuzzle**
     - ``IArena.games.SlicingPuzzle``
     - :ref:`slicing_tutorial`
     - The classic Slicing Puzzle game.
     - 1
     - Deterministic
     - Perfect information
     -

   * - **NQueens**
     - ``IArena.games.NQueens``
     - :ref:`nqueens_tutorial`
     - The classic N-Queens game.
     - 1
     - Deterministic
     - Perfect information
     - *Min score*: 0

   * - **Coins**
     - ``IArena.games.Coins``
     - :ref:`coins_tutorial`
     - Roman's coin game.
     - 2
     - Deterministic
     - Perfect information
     - **0 sum game**

   * - **Nim**
     - ``IArena.games.Nim``
     - :ref:`nim_tutorial`
     - Nim game.
     - 2
     - Deterministic
     - Perfect information
     - **0 sum game**

   * - **Tic-Tac-Toe**
     - ``IArena.games.Tic-Tac-Toe``
     - :ref:`tictactoe_tutorial`
     - Tic-Tac-Toe game (3 in a row).
     - 2
     - Deterministic
     - Perfect information
     - **0 sum game**

   * - **Mastermind**
     - ``IArena.games.Mastermind``
     - :ref:`mastermind_tutorial`
     - The classic Mastermind game.
     - 1
     - Deterministic
     - Hidden information
     -

   * - **Prisoner**
     - ``IArena.games.Prisoner``
     - :ref:`prisoner_tutorial`
     - Prisoner Dilemma 2 player game.
     - 2
     - Deterministic
     - Hidden information
     -
