.. _compassblindwalk_docs:

#################
Compass BlindWalk
#################

.. ::
  TODO: Add image
  figure:: /resources/images/c_blindwalk.png
    :scale: 30%

This game is an interactive search problem in a 2D grid.
The objective of the game is to reach the goal position from a starting position in the fewest number of steps.

This is a "Blind Walk", this means that the map is not known neither visible to the player.
The grid is an square 2D grid where each coordinate (x,y) could be a valid position or an obstacle.
In each position, the game will give the player those valid movements, that is the directions (U, D, L, R) that can be taken from the current position without hitting an obstacle.
Also, each position has a compass (U, D, L, R) indicating the closer direction of the goal from the current position.


====
Goal
====

Reach the goal position in the fewest number of steps.

-----
Score
-----

The score is ``-T`` where ``T`` is the number of steps taken to reach the goal.
The highest the score, the better.


======
Import
======

.. code-block:: python

  from IArena.games.CompassBlindWalk import CompassBlindWalkPosition
  from IArena.games.CompassBlindWalk import CompassBlindWalkMovement
  from IArena.games.CompassBlindWalk import CompassBlindWalkRules



========
Movement
========

The class ``CompassBlindWalkMovement.Direction`` defines the possible directions in the game:

- ``Up``: 0
- ``Down``: 1
- ``Left``: 2
- ``Right``: 3

The class ``CompassBlindWalkMovement`` represents a movement in the game.
This movement is a class with a single attribute ``direction``.
In order to easily create a movement, the class has 4 static methods:

- ``CompassBlindWalkMovement.up() -> CompassBlindWalkMovement``: Movement in the Up direction.
- ``CompassBlindWalkMovement.down() -> CompassBlindWalkMovement``: Movement in the Down direction.
- ``CompassBlindWalkMovement.left() -> CompassBlindWalkMovement``: Movement in the Left direction.
- ``CompassBlindWalkMovement.right() -> CompassBlindWalkMovement``: Movement in the Right direction.

In the following snippet, we create a movement in the Up direction:

.. code-block:: python

  from IArena.games.CompassBlindWalk import CompassBlindWalkMovement

  # Create Movement using the static method
  move = CompassBlindWalkMovement.up()

  # Create Movement using the constructor
  move = CompassBlindWalkMovement(direction=CompassBlindWalkMovement.Direction.Up)


========
Position
========

A position in this game holds the valid movements from the player coordinates, and the compass directions indicating the closer direction of the goal.

-------
Methods
-------

- ``valid_moves() -> List[CompassBlindWalkMovement]``: List of valid movements from the current position.
- ``compass() -> CompassBlindWalkMovement.Direction``: Direction indicating the closer direction of the goal from the current position.


In the following snippet, we represent the use of a position:

.. code-block:: python

  from IArena.games.CompassBlindWalk import CompassBlindWalkPosition

  position = ...  # Given CompassBlindWalkPosition object from game

  # Get possible valid movements
  valid_moves = position.valid_moves()  # A list of CompassBlindWalkMovement objects

  # Get compass direction
  compass_direction = position.compass()  # A single CompassBlindWalkMovement.Direction value


.. warning::

  The direction given by the compass is not always a valid movement.



=====
Rules
=====

This object defines the rules of the game.
It includes secret information about the map, the starting position, and the goal position, that is not accessible to the player.

It does not include any useful methods apart from those inherited from ``IGameRules``.
This object has few use for the player, as the information it contains is secret.


-----------
Constructor
-----------

Arguments for constructor are:

- ``map: CompassBlindWalkMap``: The map of the game as a matrix ``List[List[bool]]``.
- ``target: CompassBlindWalkCoordinate``: The target coordinate as an object that holds ``x`` and ``y`` attributes.
- ``start: CompassBlindWalkCoordinate``: The starting coordinate as an object that holds ``x`` and ``y`` attributes.


---------------
Map constructor
---------------

In order to generate a valid map that forces a path from start to target to exist,
the function ``square_valid_map_generator`` from ``IArena.utils.SquareMap`` can be used.
This function generates a random square map of given size and obstacle density,
ensuring that there is a valid path from the start to the target coordinates.

The parameters of the function are:

- ``rows: int``: Number of rows of the map.
- ``cols: int``: Number of columns of the map.
- ``start: SquareMapCoordinate``: Starting coordinate.
- ``target: SquareMapCoordinate``: Target coordinate.
- ``approx_path_length: int``: Approximate length of the path from start to target.
- ``approx_obstacle_prob: float``: Approximate probability of an obstacle in each cell.
- ``rng: RandomGenerator``: Random number generator to use.

The object ``SquareMap`` generated can be directly used as the ``map`` argument of the ``CompassBlindWalkRules`` constructor.
It also has the method ``plot_2d_map`` to visualize the map using ``matplotlib``.


==============
Useful example
==============

Let's see how to build the rules of the game in order to play an interactive game.

.. code-block:: python

  from IArena.games.CompassBlindWalk import CompassBlindWalkPosition, CompassBlindWalkMovement, CompassBlindWalkRules
  from IArena.games.CompassBlindWalk import CompassBlindWalkCoordinate
  from IArena.games.CompassBlindWalk import CompassBlindWalkMap
  from IArena.utils.SquareMap import square_valid_map_generator
  from IArena.utils.RandomGenerator import RandomGenerator
  from IArena.utils.RandomGenerator import RandomGenerator
  from IArena.arena.GenericGame import GenericGame
  from IArena.players.playable_players import PlayablePlayer

  # Set parameters
  ROW = 5
  COL = 5
  START = (0, 0)
  TARGET = (4, 4)
  APPROX_PATH_LENGTH = 12
  APPROX_OBSTACLE_PROB = 0.3
  SEED = 42
  RNG = RandomGenerator(seed=SEED)

  # Create a random valid map
  game_map = square_valid_map_generator(
      rows=ROW,
      cols=COL,
      start=CompassBlindWalkCoordinate(x=START[0], y=START[1]),
      target=CompassBlindWalkCoordinate(x=TARGET[0], y=TARGET[1]),
      approx_path_length=APPROX_PATH_LENGTH,
      approx_obstacle_prob=APPROX_OBSTACLE_PROB,
      rng=RNG
  )

  # Create the rules of the game
  rules = CompassBlindWalkRules(
      map=game_map,
      start=CompassBlindWalkCoordinate(x=START[0], y=START[1]),
      target=CompassBlindWalkCoordinate(x=TARGET[0], y=TARGET[1])
  )

  # Create a PlayablePlayer
  player = PlayablePlayer(name="Human")

  # Create the game and play
  game = GenericGame(rules=rules, players=[player])
  score = game.play()
  print(f"Final score: {score.pretty_print()}")
