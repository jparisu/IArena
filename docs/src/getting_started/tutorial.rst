.. _tutorial:

########
Tutorial
########

.. contents::
    :local:
    :backlinks: none
    :depth: 2


**IArena** is a library that implements several games, in order to allow developing AI players that can be tested on them.
In this tutorial, we will see each element involved in the player creation.
We will illustrate it by showing how to create and test a player for the game :ref:`connect4`.


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

First of all, in a game we have a :term:`Position` class.
This object, that inherits from :ref:`iposition` class, holds the current state of the game.
In the case of Connect4, the position object is ``Connect4Position``:

This ``position`` object holds 2 main variables, accessible by the following methods:

- ``next_playe()``: The next player to play, by a ``0`` or ``1`` value.
- ``get_matrix()``: The board state, by a matrix defined as ``List[List[int]]`` where:
  - ``Connect4Position.EMPTY_CELL = -1`` is an empty cell.
  - ``0`` is a player 0 token.
  - ``1`` is a player 1 token.

In the following snippet, we can see how to create an empty board and how to get the matrix and player from it:

.. code-block:: python

    from IArena.games.Connect4 import Connect4Position  # Import the Connect4Position object

    matrix = [[Connect4Position.EMPTY_CELL for _ in range(7)] for _ in range(6)]  # Create an empty 6x7 board

    position = Connect4Position(None, matrix=matrix)  # Create a position object with the empty board
    print(f'Board state: {matrix_state}')

    following_player = position.next_player()  # Get the next player to play
    print(f'Next player: {following_player}')



.. note::

    We will discuss the ``None`` parameter later.


--------
Movement
--------

In a game, we have a set of possible :term:`Movements <Movement>`.
In the case of Connect4, the movements are defined by the columns where the player can drop a token.
The movements are defined by the ``Connect4Movement`` object, an inherited class from :ref:`imovement`.
This object has the attribute ``n`` that defines the column where the token will be dropped.
For example, to drop a token in column 0, we can do:

.. code-block:: python

    from IArena.games.Connect4 import Connect4Movement  # Import the Connect4Movement class

    movement = Connect4Movement(n=0)  # Drop a token in column 0
    print(f'Movement: {movement}')



----
Game
----

Finally, we have the :term:`GameRule` class.
This object, that inherits from :ref:`igamerules`, holds the game rules and the game state.
In the case of Connect4, the game object is ``Connect4Game``.

.. code-block:: python

    from IArena.games.Connect4 import Connect4Rules  # Import the Connect4Rules class

    game = Connect4Rules()  # Create a game object


The game object has the following methods (as every other :ref:`igamerules`):

- ``n_players() -> int``: Returns the number of players.
- ``first_position() -> Connect4Position``: Returns the first position of the game.
- ``next_position(movement: Connect4Movement, position: Connect4Position) -> Connect4Position``: Returns the next position given a movement and a position.
- ``possible_movements(position: Connect4Position) -> List[Connect4Movement]``: Returns the possible movements given a position.
- ``finished(position: Connect4Position) -> bool``: Returns whether the game is finished or not.
- ``score(position: Connect4Position) -> ScoreBoard``: Returns the :term:`Score` of the game.

-------
Example
-------

Let's see an example on how to create a play of Connect4:

.. code-block:: python

    from IArena.games.Connect4 import Connect4Movement, Connect4Position, Connect4Rules

    # CREATE GAME RULES
    game = Connect4Rules()  # Default game rules

    # GET FIRST POSITION
    position = game.first_position()  # Default first position with 6x7 empty board
    print(f'Initial position: {position}')

    # GET POSSIBLE MOVEMENTS
    possible_movements = game.possible_movements(position)
    print(f'Possible movements: {" ; ".join([str(m) for m in possible_movements])}')

    # PLAY A MOVEMENT
    movement = possible_movements[0]
    position = game.next_position(movement, position)
    print(f'Next position: {position}')

    # CHECK IF GAME IS FINISHED
    finished = game.finished(position)
    print(f'Game finished: {finished}')

    # LET'S FORCE A WIN
    for i in range(3):  # Drop 3 1's tokens in column 1, and 3 0's tokens in column 0
        movement = possible_movements[1]
        position = game.next_position(movement, position)
        movement = possible_movements[0]
        position = game.next_position(movement, position)

    # CHECK IF GAME IS FINISHED
    finished = game.finished(position)
    print(f'Game {position} finished: {finished}')

    # GET SCORE
    score = game.score(position)
    print(f'Score: {score}')




======
Player
======

Now that we know how to play the game, let's create a :term:`Player`.
A player is an object of a class that inherits from :ref:`iplayer`.

----
Play
----

Every :ref:`iplayer` must implement the method ``play(position: IPosition) -> IMovement``,
where the player receives a position and must return a movement.
That is the main logic to implement in a player.

It is useful to use the rules methods in order to get the possible movements.
For this, every position has a method ``get_rules()`` that returns the rules object that generated the position.


-------------
starting_game
-------------

It is assured by the library that, for a given match, the Player will always play with the same player.
This means that, calling ``position.next_player()`` will always return the same value for the same player.

In order to create an object that is able to play multiple matches, the interface has a method ``starting_game(rules: IGameRules, player_index: int)``,
that is called by the library when the game starts.
This method is useful to set the player index in the player object, in order to know which player it is playing with.


-----------------
AI Player Example
-----------------

Let's see how to create a player for Connect4 that always plays in the first column available:

.. code-block:: python

    from IArena.interfaces.IPlayer import IPlayer
    from IArena.games.Connect4 import Connect4Movement, Connect4Position, Connect4Rules

    class MyAIPlayer(IPlayer):  # Create a class that inherits from IPlayer

        def play(self, position: Connect4Position) -> Connect4Movement:  # Implement the play method
            rules = position.get_rules()  # Get the rules object from the position
            possible_movements = rules.possible_movements(position)  # Get the possible movements
            return possible_movements[0]  # Return the first movement available


    # TEST MY PLAYER
    my_player = MyAIPlayer()

    rules = Connect4Rules()  # Default game rules
    position = game.first_position()  # Default first position with 6x7 empty board
    move = my_player.play(position)
    print(f'Movement selected: {move}')

    position = rules.next_position(move, position)
    print(f'Next position: {position}')


=====
Arena
=====

An :term:`Arena` is a kind of object that holds the game loop.
It is created by a game's rules, and enough players to play to such game.
The ``Arena`` loops by asking the players by the next move given a position, and the players must return a movement.
This ends when the game is finished, returning a :term:`Score`.

There are different types of arenas, depending on the class to use:

- ``GenericGame``: A generic arena that can be used with any game and player.
- ``BroadcastGame``: An arena that broadcasts the game state to the players in each step.
- ``ClockGame``: An arena that plays the game with a time limit for each ``play`` call for the players.

----------------
Built-in Players
----------------

The library has some built-in players that can be used to test the games.

- ``PlayablePlayer``: A player that asks the user for the movement in each step.
- ``RandomPlayer``: A player that plays randomly.
- ``ConsistentRandomPlayer``: A random player with a seed that makes it play consistently.
- ``LastPlayer``: A player that always plays the last movement available.
- etc.

--------------------
Random vs Our player
--------------------

Let's create an arena to test our player playing against a random player.
In order to see the game step by step, we will use a ``BroadcastGame`` arena.

.. code-block:: python

    from IArena.arena.GenericGame import BroadcastGame
    from IArena.players.dummy_players import ConsistentRandomPlayer

    # CREATE PLAYERS
    my_player = MyAIPlayer()
    random_player = ConsistentRandomPlayer(seed=42)

    # CREATE ARENA
    arena = BroadcastGame(
        rules=Connect4Rules(),  # Default game rules
        players=[my_player, random_player]  # Our player and a random player
    )

    # PLAY
    score = arena.play()
    print(f'Score: {score}')



--------------------------
Play against our AI player
--------------------------

We can also play against our own player to see how it behaves.
We can use the generic ``PlayablePlayer``, but we will better use a specific player made for Connect 4:

.. code-block:: python

    from IArena.arena.GenericGame import GenericGame
    from IArena.games.Connect4 import Connect4PlayablePlayer

    # CREATE PLAYERS
    my_player = MyAIPlayer()
    human_player = Connect4PlayablePlayer()

    # CREATE ARENA
    arena = GenericGame(
        rules=Connect4Rules(),  # Default game rules
        players=[my_player, human_player]  # Our player and a human player
    )

    # PLAY
    score = arena.play()
    print(f'Score: {score}')


----------------------
Set specific positions
----------------------

In order to test a specific position, we can set the position in the rules, by setting an initial position.
This is useful to test our AI players in specific situations.

Short str board representation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :ref:`connect4` game has a short string representation of the board to make it easier to create positions.
This representation is a string as:

- First value ``0`` or ``1`` for the next player.
- Then the number of rows
- Finally, a stack of values ``0`` or ``1``.
- Every value separated by ``|``.

*For example, the default empty board is:* ``0|6||||||||``.


The ``Connect4Position`` class has 2 methods to convert from a matrix to a short str and vice versa:

- ``convert_short_str_to_matrix_str(short_str: str) -> str``: Converts a short str to a matrix str.
- ``convert_short_str_to_matrix(short_str: str) -> List[List[int]]``: Converts a short str to a matrix.

And a position can be created from a short str by using ``Connect4Position.from_str(rules: Connect4Rules, short_str: str) -> Connect4Position``.

Let's see how to use this functions to check what position a short str represents, and how to create a position from it:

.. code-block:: python

    from IArena.games.Connect4 import Connect4Position

    # CREATE POSITION FROM SHORT STR
    short_str = '0|6|111|111|111||0111|0111|0111|'
    position = Connect4Position.from_str(None, short_str)
    print(f'Position: {position}')

    # CONVERT POSITION TO SHORT STR
    s = str(position.position)
    print(f'Short str: {s}')


==========
Tournament
==========

Finally, there is a special arena that is able to play several games in a row, in order to generate a better approach of how good a player is.
This is the ``TournamentGame`` class.

Let's compare our player with 2 other players: a random one and a last player.

.. code-block:: python

    from IArena.arena.TournamentGame import TournamentGame
    from IArena.players.dummy_players import ConsistentRandomPlayer, LastPlayer

    # CREATE PLAYERS
    my_player = MyAIPlayer(name="My Player")
    random_player = ConsistentRandomPlayer(seed=42, name="Random Player")
    last_player = LastPlayer("Last Player")

    # CREATE ARENA
    arena = TournamentGame(
        rules=Connect4Rules(),  # Default game rules
        players=[my_player, random_player, last_player],  # Players
        matches=100  # Number of games to play
    )

    # PLAY
    scores = arena.play()
    print(f'Scores: {scores}')
