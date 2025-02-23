.. _tutorial:

########
Tutorial
########

**IArena** is a library that implements several games, in order to allow developing AI players that can be tested on them.
In this tutorial, we will see each element involved in the player creation.
We will illustrate it by showing how to create and test a player for the game :ref:`connect4_tutorial`.


============
Installation
============

In order to work with **IArena**, you need to install it.
You can do it by running the following command:

.. code-block:: bash

    pip install --upgrade git+https://github.com/jparisu/IArena.git

or by adding the following line in a Jupyter notebook:

.. code-block:: python

    %pip install --upgrade git+https://github.com/jparisu/IArena.git

For more installation options, please refer to :ref:`installation`.


====
Game
====

First of all, let's focus on the game we want to play.
For this example, we will use the game Connect4.
However, this is extrapolated to any other game implemented in **IArena**.

--------
Position
--------

First of all, in a game we have a :term:`Position` object.
This object, that inherits from :ref:`iposition` class, holds the current state of the game.
In the case of Connect4, the position object is ``Connect4Position``:

.. code-block:: python

    from IArena.games.Connect4 import Connect4Position

    position = Connect4Position(None)  # Create an empty board

.. note::

    We will discuss the ``None`` parameter later.


This ``position`` object holds 2 main variables:

- The next player to play, by a ``0`` or ``1`` value.
- The board state, by a matrix defined as ``List[List[int]]`` where:
  - ``Connect4Position.EMPTY_CELL = -1`` is an empty cell.
  - ``0`` is a player 0 token.
  - ``1`` is a player 1 token.

In the following snippet, we can see how to create an empty board and how to get the matrix and player from it:

.. code-block:: python

    from IArena.games.Connect4 import Connect4Position

    position = Connect4Position(None)

    following_player = position.next_player()
    print(f'Next player: {following_player}')

    matrix_state = position.get_matrix()
    print(f'Board state: {matrix_state}')
