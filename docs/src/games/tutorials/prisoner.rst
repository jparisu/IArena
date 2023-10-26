.. _prisoner_tutorial:

################
Prisoner Dilemma
################

.. figure:: /resources/images/prisoner.png

This game is the classical Prisoner Dilemma.
The objective of the game is minimize your value.
The game is played by two players, each one chooses between two options: cooperate or defect.
The value of each player depends on the combination of the actions of both players.


====
Goal
====

Minimize the value of the player.

-----
Score
-----

The score is calculated following the :ref:`score table <prisoner_tutorial_scoretable>`.


======
Import
======

.. code-block:: python

  import IArena.games.PrisonerDilemma.PrisonerDilemmaPosition as PrisonerDilemmaPosition
  import IArena.games.PrisonerDilemma.PrisonerDilemmaMovement as PrisonerDilemmaMovement
  import IArena.games.PrisonerDilemma.PrisonerDilemmaRules as PrisonerDilemmaRules


========
Movement
========

A movement is an ``int`` where ``0`` means cooperate and ``1`` means defect.

- ``decision``
  - ``int``
  - ``0, 1``
  - 0: Cooperate
  - otherwise: Defect


.. code-block:: python

  # Decide to cooperate
  movement = PrisonerDilemmaMovement.cooperate()
  # or
  movement = PrisonerDilemmaMovement(PrisonerDilemmaMovement.Cooperate)
  # or
  movement = PrisonerDilemmaMovement(0)

  # Decide to defect
  movement = PrisonerDilemmaMovement.defect()
  # or
  movement = PrisonerDilemmaMovement(PrisonerDilemmaMovement.Defect)
  # or
  movement = PrisonerDilemmaMovement(1)


========
Position
========

A position has nothing to store.
The rules are stored within the rules


=====
Rules
=====

This games has every methods of :ref:`IRules <infrastructure_rules>`.

It counts with 1 method to retrieve the score matrix:

- ``rules.get_score_table() -> PrisonerDilemmaScoreTable``


-----------
Constructor
-----------

To construct the rules, it can give the score table, or let it be creater randomly:

#. Using a secret code already defined.

  .. code-block:: python

    # Random score table with seed=0
    rules = PrisonerDilemmaRules(seed=0)

    # Score table with values {Cooperate:{Cooperate: 1, Defect: 6}, Defect:{Cooperate: 2, Defect: 4}}
    rules = PrisonerDilemmaRules(score_table=
      {
        PrisonerDilemmaMovement.Cooperate:
          {
            PrisonerDilemmaMovement.Cooperate: 1,
            PrisonerDilemmaMovement.Defect: 6
          },
        PrisonerDilemmaMovement.Defect:
          {
            PrisonerDilemmaMovement.Cooperate: 2,
            PrisonerDilemmaMovement.Defect: 4
          },
      }
    )



.. _prisoner_tutorial_scoretable:

-----------
Score Table
-----------

The score of the player is calculated depending a score matrix that is defined in the rules.
The score matrix is a matrix of size 2x2 of floats like the following:

.. code-block:: python

  # score_table = PrisonerDilemmaScoreTable
  score_table PrisonerDilemmaScoreTable(score_table=
    {
      PrisonerDilemmaMovement.Cooperate:
        {
          PrisonerDilemmaMovement.Cooperate: A,
          PrisonerDilemmaMovement.Defect: B
        },
      PrisonerDilemmaMovement.Defect:
        {
          PrisonerDilemmaMovement.Cooperate: C,
          PrisonerDilemmaMovement.Defect: D
        },
    }
  )

  # a = PrisonerDilemmaMovement
  # b = PrisonerDilemmaMovement
  x = score_table.score(player_movement=a, opponent_movement=b) # float
