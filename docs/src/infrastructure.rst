.. _infrastructure:

##############
Infrastructure
##############

================
Project Overview
================

Detailed information about the project.

.. _infrastructure_interfaces:

==================
Library Interfaces
==================


.. _infrastructure_rules:

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
    - *Yes*.

  * - ``first_position()``.
    - The initial position.
    - *Yes*.

  * - ``next_position()``.
    - The possible moves giving a position.
    - *Yes*.

  * - ``possible_movements()``.
    - The next position giving a position and a move.
    - *Yes*.

  * - ``finished()``.
    - Whether a position is terminal.
    - *Yes*.

  * - ``score()``.
    - The score of a terminal position.
    - *Yes*.

  * - ``is_movement_possible()``.
    - Whether a move is possible giving a position.
    - *No*.
