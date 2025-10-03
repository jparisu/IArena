.. _tutorial:

########
Tutorial
########

.. contents::
    :local:
    :backlinks: none
    :depth: 2


**IArena** is a library that implements several games, in order to allow developing AI players that can be tested on them.
In this tutorial, we will see each element involved in the player creation.
We will illustrate it by showing how to create and test a player for the game :ref:`Mastermind`.


============
Installation
============

In order to work with **IArena**, you need to install it.
You can do it by running the following command:

.. code-block:: bash

    pip install --upgrade git+https://github.com/jparisu/IArena.git

or by adding the following line in a Jupyter notebook:

.. code-block:: python

    %pip install --upgrade git+https://github.com/jparisu/IArena.git

For more installation options, please refer to :ref:`installation`.


====
Game
====

First of all, let's focus on the game we want to play.
For this example, we will use the game :ref:`mastermind_docs`.
However, this is extrapolated to any other game implemented in **IArena**.


--------
Movement
--------

First of all, in a game we have a :term:`Movement` class.
In the case of Mastermind, the movements are defined by a guess of the secret code.
The movements are defined by the ``MastermindMovement`` object, an inherited class from :ref:`imovement`.
This object has the attribute ``guess`` that defines a list of integers representing the guess.
For example, in a game with 7 possible numbers, and a code of length 4, a guess could be: ``[0, 1, 2, 3]`` or ``[6, 5, 4, 3]``.

.. code-block:: python

    from IArena.games.Mastermind import MastermindMovement  # Import the MastermindMovement class

    movement = MastermindMovement(guess=[0, 1, 2, 3])  # Guess the code [0, 1, 2, 3]
    print(f'Movement: {movement}')



--------
Position
--------

In a game we have a :term:`Position` class.
This object, that inherits from :ref:`iposition` class, holds the current state of the game.
In the case of Mastermind, the position object is ``MastermindPosition``, that holds the list of guesses done so far, and their correctness.

MastermindCorrectness
^^^^^^^^^^^^^^^^^^^^^

First let's see an auxiliary class: ``MastermindCorrectness``.
This is an enumeration to indicate the correctness of a number in a code with the following values:
- ``Wrong``: 0
- ``Misplaced``: 1
- ``Correct``: 2


Each ``position`` object holds 2 main variables, accessible by the following methods:

- ``guesses()``: The list of guesses done so far. This returns a list ``List[MastermindMovement]``:
    - The first guess is ``guesses()[0]``.
    - The last guess is ``guesses()[-1]``.
    - To access the last guess, there is also the method ``last_guess()``.
- ``correctness()``: A list with a value per guess indicating those numbers that are correct, misplaced or wrong. This returns a list ``List[List[MastermindCorrectness]]``:
    - The correctness of the first guess is ``correctness()[0]``.
    - The correctness of the last guess is ``correctness()[-1]``.
    - To access the correctness of the last guess, there is also the method ``last_correctness()``.
    - Each correctness is a list of ``MastermindCorrectness`` with the same length as the guess. This indicates for each number in the guess, if it is correct, misplaced or wrong.

In the following snippet, we can see how to create an empty board and how to get the matrix and player from it:

.. code-block:: python

    from IArena.games.Mastermind import MastermindPosition  # Import the MastermindPosition object

    # Let's recreate a position on a game with 7 possible numbers and a code of length 4
    guess_0 = MastermindMovement(guess=[0, 1, 2, 3])  # First guess
    guess_1 = MastermindMovement(guess=[0, 2, 4, 5])  # Second guess

    # Let's imagine that the secret code was [0, 2, 5, 6]. The correctness would be:
    correctness_0 = [2, 0, 1, 0]  # Correctness of the first guess: 0 is correct, 1 is wrong, 2 is misplaced, 3 is wrong
    correctness_1 = [2, 2, 0, 1]  # Correctness of the second guess: 0 is correct, 2 is correct, 4 is wrong, 5 is misplaced

    # Create a position with 2 guesses and their correctness
    # This is the object that will be passed to the player in order to play
    position = MastermindPosition(
        rules=None,  # We will discuss this parameter later
        guesses=[guess_0, guess_1],  # List of guesses done so far
        correctness=[correctness_0, correctness_1]  # List of correctness of the guesses done so far
    )

    # Get the last guess tried
    last_guess = position.last_guess()

    # Get the correctness of the last guess
    last_correctness = position.last_correctness()

    # Check how many numbers on the last guess are correct
    n_correct = sum(1 for c in last_correctness if c == MastermindPosition.MastermindCorrectness.Correct)



.. note::

    The ``None`` parameter representes the rules of the game that generated the position.
    We will discuss it later.


----
Game
----

Finally, we have the :term:`GameRule` class.
This object, that inherits from :ref:`igamerules`, holds the game rules and the game state.
In the case of Mastermind, the game object is ``MastermindGame``.

In order to create a game object, ``MastermindGame`` requires the following parameters:

- ``code_size: int``: Length of the secret code (N).
- ``number_colors: int``: Number of different values available (M). If no repetitions allowed, M >= N.
- ``secret: List[int]``: A list of size (N) with integers between 0 and M-1 representing the secret code.
- ``allow_repetitions: bool``: Whether the secret code can have repeated values.

``MastermindGame`` also counts with a static method that generates a random secret code: ``random_secret`` with the following parameters:

- ``code_size: int``: Length of the secret code (N).
- ``number_colors: int``: Number of different values available (M). If no repetitions allowed, M >= N.
- ``rng: RandomGenerator``: A random generator to generate the secret code.
- ``color_repetition: bool``: Whether the secret code can have repeated values.

Let's see an example on how to create a game object with a random secret code:

.. code-block:: python

    from IArena.games.Mastermind import MastermindRules  # Import the MastermindRules class

    # Create a game object with default values: N = 5, M = 8, no repetitions, random secret code
    game = MastermindRules()

    # Create a game object with specific values: N = 4, M = 7, repetitions allowed, random secret code
    game = MastermindRules(code_size=4, number_colors=7, allow_repetitions=True, secret=[0, 2, 5, 6])



The game object has the following methods (as every other :ref:`igamerules`):

- ``n_players() -> int``: Returns the number of players.
- ``first_position() -> MastermindPosition``: Returns the first position of the game.
- ``next_position(movement: MastermindMovement, position: MastermindPosition) -> MastermindPosition``: Returns the next position given a movement and a position.
- ``possible_movements(position: MastermindPosition) -> List[MastermindMovement]``: Returns the possible movements given a position.
- ``finished(position: MastermindPosition) -> bool``: Returns whether the game is finished or not.
- ``score(position: MastermindPosition) -> ScoreBoard``: Returns the :ref:`scoreboard` of the game.


Apart from class methods, ``MastermindRules`` has the following specific methods:

- ``get_number_colors()``: Get value (N).
- ``get_size_code()``: Get value (M).
- ``allow_repetition()``: Whether repetitions are allowed in the secret code.


-------
Example
-------

Let's see an example on how to create a play of Mastermind:

.. code-block:: python

    from IArena.games.Mastermind import MastermindMovement, MastermindPosition, MastermindRules

    # CREATE GAME RULES
    # Create a game object with specific values: N = 4, M = 7, repetitions not allowed, random secret code
    game = MastermindRules(code_size=4, number_colors=7, allow_repetitions=False, secret=[0, 2, 5, 6])

    # GET FIRST POSITION
    position = game.first_position()  # Default first position with 6x7 empty board
    print(f'Initial position: {position}')

    # GET POSSIBLE MOVEMENTS
    possible_movements = list(game.possible_movements(position))
    print(f'Possible movements: {" ; ".join([str(m) for m in possible_movements])}')
    # WARNING: possible_movements returns an iterator that may contain a large number of movements !!

    # PLAY A MOVEMENT
    movement = possible_movements[0]
    position = game.next_position(movement, position)
    print(f'Next position: {position}')

    # CHECK IF GAME IS FINISHED
    finished = game.finished(position)
    print(f'Game finished: {finished}')

    # LET'S FORCE A WIN
    winning_movement = MastermindMovement(guess=[0, 2, 5, 6])  # The secret code
    position = game.next_position(winning_movement, position)
    print(f'Next position (winning): {position}')

    # CHECK IF GAME IS FINISHED
    finished = game.finished(position)
    print(f'Game {position} finished: {finished}')

    # GET SCORE
    score = game.score(position)
    print(f'Score:\n{score.pretty_print()}')

    # GET THE SCORE OF MY PLAYER
    my_score = score[0]
    # my_score = score.get_score(0)  # This line is equivalent to the previous one
    print(f'My score: {my_score}')



====
Play
====

If you want to play the game manually, you can use the built-in :ref:`PlayablePlayer` class for Mastermind: ``MastermindPlayablePlayer``.
Next, we see how to create a playable game for mastermind:

.. code-block:: python

    from IArena.games.Mastermind import MastermindMovement, MastermindPosition, MastermindRules
    from IArena.arena.GenericGame import GenericGame

    # PARAMETERS
    code_size = 4
    number_colors = 7
    allow_repetitions = False
    secret = [0, 2, 5, 6]  # Set None to use a random secret

    # Create game rules
    game = MastermindRules(code_size=code_size, number_colors=number_colors, allow_repetitions=allow_repetitions, secret=secret)

    # Create Player
    player = MastermindPlayablePlayer(name="Human")

    # Activate game loop
    game = GenericGame(rules=rules, players=[player])
    score = game.play()
    print(score.pretty_print())



=======
IPlayer
=======

Now that we know how to play the game, let's create a :term:`Player`.
A player is an object of a class that inherits from :ref:`iplayer`.

----
Play
----

Every :ref:`iplayer` must implement the method ``play(position: IPosition) -> IMovement``,
where the player receives a position and must return a movement.
That is the main logic to implement in a player.

It is useful to use the rules methods in order to get the possible movements.
For this, every position has a method ``get_rules()`` that returns the rules object that generated the position.


-------------
starting_game
-------------

It is assured by the library that, for a given match, the Player will always play with the same player.
This means that, calling ``position.next_player()`` will always return the same value for the same player.

In order to create an object that is able to play multiple matches, the interface has a method ``starting_game(rules: IGameRules, player_index: int)``,
that is called by the library when the game starts.
This method is useful to reset the player for a new game if needed.


-----------------
AI Player Example
-----------------

Let's see how to create a player for Mastermind that always plays in the first column available:

.. code-block:: python

    from IArena.interfaces.IPlayer import IPlayer
    from IArena.games.Mastermind import MastermindMovement, MastermindPosition, MastermindRules

    class MyAIPlayer(IPlayer):  # Create a class that inherits from IPlayer

        def play(self, position: MastermindPosition) -> MastermindMovement:  # Implement the play method
            rules = position.get_rules()  # Get the rules object from the position
            possible_movements = rules.possible_movements(position)  # Get the possible movements
            return next(possible_movements)  # Return the first movement available


    # TEST MY PLAYER
    my_player = MyAIPlayer()

    rules = MastermindRules()  # Default game rules
    position = game.first_position()  # Default first position with random secret
    move = my_player.play(position)
    print(f'Movement selected: {move}')

    position = rules.next_position(move, position)
    print(f'Next position: {position}')


=====
Arena
=====

An :term:`Arena` is a kind of object that holds the game loop.
It is created by a game's rules, and enough players to play to such game.
The ``Arena`` loops by asking the players by the next move given a position, and the players must return a movement.
This ends when the game is finished, returning a :term:`Score`.

There are different types of arenas, depending on the class to use:

- ``GenericGame``: A generic arena that can be used with any game and player.
- ``BroadcastGame``: An arena that broadcasts the game state to the players in each step. Use this arena to see the game development for an AI player.
- ``ClockGame``: An arena that plays the game with a time limit for each ``play`` call for the players.
