.. _getting_started:

###############
Getting Started
###############

================
Project Overview
================

.. warning::

    Coming soon.


============
Installation
============

Check the :ref:`installation guide <installation>`.


=====
Games
=====

To check the games available in the library, please check the :ref:`games_available` section.


===========
Play a game
===========

There is an specific *arena* that allows to play any game in a terminal interface.
In order to do so follow this instructions with the game desired:

.. code-block:: python

    # Change Hanoi for the name of the game to play

    from IArena.arena.PlayableGame import PlayableGame
    from IArena.games.Hanoi import HanoiRules, HanoiMovement, HanoiPosition

    # Create the game and play it
    rules = HanoiRules()
    game = PlayableGame(rules)
    score = game.play()


==============
Build a player
==============

In order to build a new player, ``IPlayer`` must be implemented.
Check the :ref:`players` section for more information.


=====
Games
=====

To check the games available in the library, please check the :ref:`games_available` section.


==============
Add a new game
==============

.. warning::

    Coming soon.


========
Tutorial
========

To get a more detailed tutorial, check the :ref:`tutorial` section.
