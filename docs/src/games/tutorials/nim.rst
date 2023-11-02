.. _nim_tutorial:

###
Nim
###

.. figure:: /resources/images/nim.svg
    :scale: 40%

This game is a classical 2 players game called *Nim*.
There are ``N`` rows with ``Ni`` sticks in each row.
By turns, each player takes as much sticks as he wants from a single row.
The player that takes the last stick loses.

This is a **0 sum** game with perfect information.

====
Goal
====

The goal of this game is not to be the last player to take a stick.

-----
Score
-----

- The player that takes the last stick:
  - ``1``
- The player that cannot take a stick:
  - ``0``

======
Import
======

.. code-block:: python

  from IArena.games.Nim import NimPosition
  from IArena.games.Nim import NimMovement
  from IArena.games.Nim import NimRules


========
Movement
========

A movement is represented by 2 ``int`` representing the number of the row and the number of sticks:

- ``line_index``
  - ``int``
  - ``0 <= line_index < N``
  - Index of the line to remove sticks
- ``remove``
  - ``int``
  - ``0 < remove < Ni``
  - Number of sticks to remove from the line (must be less than the number of sticks in the line)

.. code-block:: python

    movement = NimMovement(
      line_index=2,
      remove=1)
    # Remove 1 stick from the 3rd line


========
Position
========

A position is represented by a ``list`` of ``int`` describing each row:

.. code-block:: python

  # position : NimPosition
  len(position)      # Number of rows
  position[0]        # Number of sticks in the first row

  lines = position.lines
  len(lines)         # Number of rows
  lines[0]           # Number of sticks in the first row


=====
Rules
=====

This games has every methods of :ref:`IRules <infrastructure_rules>`.


-----------
Constructor
-----------

Can receive 1 argument:

- ``original_lines``
  - ``List[int]``
  - The amount of sticks in the first position
  - Default: ``[1,3,5,7]``


.. code-block:: python

  # Start default game [1,3,5,7]
  rules = NimRules()

  # Start game with 3 rows of 5 sticks
  rules = NimRules(
    original_lines=[5,5,5])
