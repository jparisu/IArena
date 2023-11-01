.. _players:

#######
Players
#######

The final goal of this project is to be able to create software that can play a specific game.
This software is called **player** and must implement the **IPlayer** interface.

=======
IPlayer
=======

The interface can be found in ``src/IArena/interfaces/IPlayer`` module.

This interface is used by an *arena* to play a specific set of rules.
The only method that must be implemented is ``play``.
It receives an ``IPosition`` and must return an ``IMovement`` (specific movement depending on the rules playing).

.. code-block:: python

    def play(
            self,
            position: IPosition) -> IMovement:
        pass

The constructor of an ``IPlayer`` is not defined.
Each implementation could have its own constructor, adding for example a name, the rules of the game, etc.

-----
Rules
-----

The rules of each game are available from each ``IPosition`` of the game by calling ``position.get_rules()``.

---------
Movements
---------

Choose the next movement is responsibility of the player.
Each game has different movements that require different parameters.
Depending on the game, the player must create a movement with the required parameters.

However, in the rules of the game there is a method ``possible_movements`` that returns a list of possible movements.
The player can create its own movement or choose one from the list of possible movements.

.. code-block:: python

    from IArena.interfaces.IPlayer import IPlayer

    class MyPlayer(IPlayer):

        def play(
                self,
                position: IPosition) -> IMovement:

            # Create next movement from scratch
            movement = IMovement(...)

            # Choose one from the list of possible movements
            rules = position.get_rules()
            possible_movements = rules.possible_movements(position)
            movement = possible_movements[...]


-----
Arena
-----

In order to play a game with an autonomous player, an *arena* is required.
An *Arena* is a class that implements the loop of the game, or the context in which the game is played.
For further information, see the :ref:`arena` module.

The easiest arena to use is ``GenericGame`` that implements a single loop over the game and make each player play in its turn.
If you prefer to see step by step the game playing by the player, use ``BroadcastGame``.

.. code-block:: python

    from IArena.arena.GenericGame import GenericGame  # or BroadcastGame
    from IArena.games.Hanoi import HanoiRules, HanoiMovement, HanoiPosition

    rules = HanoiRules()
    my_player = MyPlayer()

    arena = GenericGame(
        rules=rules,
        players=[my_player]
    )
    score = arena.play()


Multiplayer games
^^^^^^^^^^^^^^^^^

In games with more than 1 player, you would need another player to play against.
There are several generic players implemented, please check :ref:`random_player`.


.. code-block:: python

    from IArena.arena.GenericGame import GenericGame  # or BroadcastGame
    from IArena.games.Coins import CoinsRules, CoinsMovement, CoinsPosition
    from IArena.players.players import RandomPlayer

    rules = CoinsRules()
    my_player = MyPlayer()
    other_player = RandomPlayer()

    arena = GenericGame(
        rules=rules,
        players=[my_player, other_player]
    )
    score = arena.play()
