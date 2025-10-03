.. _players:

#######
Players
#######

The final goal of this project is to be able to create software that can play a specific game.
This software is called **player** and must implement the **IPlayer** interface.

.. _iplayer:

=======
IPlayer
=======

The interface can be found in ``src/IArena/interfaces/IPlayer`` module.
This interface is used by an *arena* to play a specific set of rules.

-------
Methods
-------

``play``
^^^^^^^^

The only **required** method that must be implemented is ``play``.
It receives an ``IPosition`` and must return an ``IMovement`` (specific movement depending on the rules playing).

.. code-block:: python

    def play(
            self,
            position: IPosition) -> IMovement:
        pass

``name``
^^^^^^^^

There is a method ``name`` that returns a string with the name of the player.
The default constructor has the argument ``name`` that sets the internal ``_name`` attribute.

``starting_game``
^^^^^^^^^^^^^^^^^

The method ``starting_game`` is called by the ``arena`` when the game starts.
It is useful to set, for example, the index of the player in the game.


.. code-block:: python

    def starting_game(
            self,
            rules: IGameRules,
            player_index: int):
        pass


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
    from IArena.games.Hanoi import HanoiRules, HanoiMovement, HanoiPosition

    class MyPlayer(IPlayer):

        def play(
                self,
                position: HanoiPosition) -> HanoiMovement:

            # Create next movement from scratch
            movement = IMovement(...)

            # Choose one from the list of possible movements
            rules = position.get_rules()
            possible_movements = rules.possible_movements(position)
            movement = possible_movements[...]

            # Return the movement
            return movement


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
    from IArena.games.Hanoi import HanoiRules

    rules = HanoiRules()
    my_player = MyPlayer()

    arena = GenericGame(
        rules=rules,
        players=[my_player]
    )
    score = arena.play()


.. _playable_player:

==============
PlayablePlayer
==============

A ``PlayablePlayer`` is a special type of player that allows a human to play the game manually using a simple text interface.
It implements the ``IPlayer`` interface and can be used in any arena.
It is useful to test the rules of a game or to play against an autonomous player.

.. code-block:: python

    from IArena.players.playable_players import PlayablePlayer
    from IArena.games.Hanoi import HanoiRules
    from IArena.arena.GenericGame import GenericGame

    # Create a playable player
    human_player = PlayablePlayer()

    # Create the game
    rules = HanoiRules()

    # Create the arena
    arena = GenericGame(
        rules=rules,
        players=[my_player]
    )

    # Activate the arena
    score = arena.play()


--------------
Custom players
--------------

Several games have custom players that implement the ``PlayablePlayer`` interface.
These players have a better interface adapted to the specific game.
Some examples are:

- ``MastermindPlayablePlayer`` in ``IArena.games.Mastermind``. Documentation: :ref:`mastermind_playable_player`


For further information, see the documentation of each game.
