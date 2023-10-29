.. _highestcard_tutorial:

############
Highest Card
############

.. figure:: /resources/images/cards.jpeg
    :scale: 80%

This game is a card game with ``N`` players and ``NxM`` cards.
The objective of the game is to guess the number of rounds that the player will win with its ``M`` cards.
Each player guesses in secret at the begining knowing only their ``M`` cards, for how many rounds it will win.
Then, ``M`` rounds are played in which each player plays its highest card.
The player that gets closer to the real number of rounds that it wins without passing it, wins the game.


====
Goal
====

Guess the number of rounds your card will be the higher, trying not to pass it.

-----
Score
-----

The score is calculated as:

- If the player guesses correctly, it gets ``-5`` point.
- If the player guesses lower than the real number, it gets ``1`` point for each round it passes.
- If the player guesses higher than the real number, it gets ``2`` point for each round it passes.


======
Import
======

.. code-block:: python

  import IArena.games.HighestCard.HighestCardPosition as HighestCardPosition
  import IArena.games.HighestCard.HighestCardMovement as HighestCardMovement
  import IArena.games.HighestCard.HighestCardRules as HighestCardRules


========
Movement
========

A movement is an ``int`` with the guess of number of rounds:

- ``bet``
  - ``int``
  - ``0 <= bet <= M``
  - Number of rounds it guesses it will win


.. code-block:: python

  # For guessing 0 rounds win
  movement = HighestCardMovement(bet=0)

  # For guessing 3 rounds win
  movement = HighestCardMovement(bet=3)


========
Position
========

Each player can get its cards from the position, and only its cards.

.. code-block:: python

  # position = HighestCardPosition

  # For getting the cards of the player
  cards = position.get_cards()

  # Get first card
  card = cards[0]


=====
Rules
=====

This games has every methods of :ref:`IRules <infrastructure_rules>`.

It counts with 2 method to retrieve the values of the game

- ``rules.n_players() -> int``
- ``rules.m_cards() -> int``


-----------
Constructor
-----------

The rules can be created with the cards already deal or with a seed to generate random decks.

  .. code-block:: python

    # Default game
    rules = HighestCardRules()
    # or
    rules = HighestCardRules(n_players=3, m_cards=4)

    # Replicable game
    rules = HighestCardRules(n_players=3, m_cards=4, seed=0)

    # With cards already deal for 2 player game with 2 cards
    cards_distribution = {0: [0, 1], 1: [2, 3]}
    rules = HighestCardRules(cards_distribution=cards_distribution)
