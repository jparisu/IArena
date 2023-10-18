.. _games:

#####
Games
#####

In this module there are described and explained the different games supported so far by the library.

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

   * - **Mastermind**
     - ``IArena.games.Mastermind``
     - :ref:`mastermind_tutorial`
     - The classic Mastermind game.
     - 1
     - Deterministic
     - Hidden information
     -
