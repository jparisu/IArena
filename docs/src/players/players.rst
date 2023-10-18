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

    def play(
            self,
            position: IPosition) -> IMovement:

        # Create next movement from scratch
        movement = IMovement(...)

        # Choose one from the list of possible movements
        rules = position.get_rules()
        possible_movements = rules.possible_movements(position)
        movement = possible_movements[...]
