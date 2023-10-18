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
