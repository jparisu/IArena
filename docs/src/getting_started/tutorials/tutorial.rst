.. _tutorial:

###############
Wordle Tutorial
###############

.. contents::
    :local:
    :backlinks: none
    :depth: 2


**IArena** is a library that implements several games, in order to allow developing AI players that can be tested on them.
In this tutorial, we will see each element involved in the player creation.
We will illustrate it by showing how to create and test a player for the game :ref:`Wordle <wordle_docs>`.


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
For this example, we will use the game :ref:`wordle_docs`.
However, this is extrapolated to any other game implemented in **IArena**.


--------
Movement
--------

First of all, in a game we have a :term:`Movement` class.
In the case of Wordle, the movements are defined by a guess of the secret code.
The movements are defined by the ``WordleMovement`` object, an inherited class from :ref:`imovement`.
This object has the attribute ``guess`` that defines a list of integers representing the guess.
For example, in a game with 7 possible numbers, and a code of length 4, a guess could be: ``[0, 1, 2, 3]`` or ``[6, 5, 4, 3]``.

.. code-block:: python

    from IArena.games.Wordle import WordleMovement  # Import the WordleMovement class

    movement = WordleMovement(guess=[0, 1, 2, 3])  # Guess the code [0, 1, 2, 3]
    print(f'Movement: {movement}')



--------
Position
--------

In a game we have a :term:`Position` class.
This object, that inherits from :ref:`iposition` class, holds the current state of the game.
In the case of Wordle, the position object is ``WordlePosition``, that holds the list of guesses done so far, and their feedback.

WordleFeedback
^^^^^^^^^^^^^^

First let's see an auxiliary class: ``WordleFeedback``.
This is an enumeration to indicate the feedback of a number in a code with the following values:
- ``Wrong``: 0
- ``Misplaced``: 1
- ``Correct``: 2


Each ``position`` object holds 2 main variables, accessible by the following methods:

- ``guesses()``: The list of guesses done so far. This returns a list ``List[WordleMovement]``:
    - The first guess is ``guesses()[0]``.
    - The last guess is ``guesses()[-1]``.
    - To access the last guess, there is also the method ``last_guess()``.
- ``feedback()``: A list with a value per guess indicating those numbers that are correct, misplaced or wrong. This returns a list ``List[List[WordleFeedback]]``:
    - The feedback of the first guess is ``feedback()[0]``.
    - The feedback of the last guess is ``feedback()[-1]``.
    - To access the feedback of the last guess, there is also the method ``last_feedback()``.
    - Each feedback is a list of ``WordleFeedback`` with the same length as the guess. This indicates for each number in the guess, if it is correct, misplaced or wrong.

In the following snippet, we can see how to create an empty board and how to get the matrix and player from it:

.. code-block:: python

    from IArena.games.Wordle import WordlePosition  # Import the WordlePosition object

    # Let's recreate a position on a game with 7 possible numbers and a code of length 4
    guess_0 = WordleMovement(guess=[0, 1, 2, 3])  # First guess
    guess_1 = WordleMovement(guess=[0, 2, 4, 5])  # Second guess

    # Let's imagine that the secret code was [0, 2, 5, 6]. The feedback would be:
    feedback_0 = [2, 0, 1, 0]  # Feedback of the first guess: 0 is correct, 1 is wrong, 2 is misplaced, 3 is wrong
    feedback_1 = [2, 2, 0, 1]  # Feedback of the second guess: 0 is correct, 2 is correct, 4 is wrong, 5 is misplaced

    # Create a position with 2 guesses and their feedback
    # This is the object that will be passed to the player in order to play
    position = WordlePosition(
        rules=None,  # We will discuss this parameter later
        guesses=[guess_0, guess_1],  # List of guesses done so far
        feedback=[feedback_0, feedback_1]  # List of feedback of the guesses done so far
    )

    # Get the last guess tried
    last_guess = position.last_guess()

    # Get the feedback of the last guess
    last_feedback = position.last_feedback()

    # Check how many numbers on the last guess are correct
    n_correct = sum(1 for c in last_feedback if c == WordlePosition.WordleFeedback.Correct)



.. note::

    The ``None`` parameter represents the rules of the game that generated the position.
    We will discuss it later.


----
Game
----

Finally, we have the :term:`GameRule` class.
This object, that inherits from :ref:`igamerules`, holds the game rules and the game state.
In the case of Wordle, the game object is ``WordleGame``.

In order to create a game object, ``WordleGame`` requires the following parameters:

- ``code_size: int``: Length of the secret code (N).
- ``number_values: int``: Number of different values available (M). If no repetitions allowed, M >= N.
- ``secret: List[int]``: A list of size (N) with integers between 0 and M-1 representing the secret code.
- ``allow_repetition: bool``: Whether the secret code can have repeated values.

``WordleGame`` also counts with a static method that generates a random secret code: ``random_secret`` with the following parameters:

- ``code_size: int``: Length of the secret code (N).
- ``number_values: int``: Number of different values available (M). If no repetitions allowed, M >= N.
- ``rng: RandomGenerator``: A random generator to generate the secret code.
- ``allow_repetition: bool``: Whether the secret code can have repeated values.

Let's see an example on how to create a game object with a random secret code:

.. code-block:: python

    from IArena.games.Wordle import WordleRules  # Import the WordleRules class

    # Create a game object with default values: N = 5, M = 8, no repetitions, random secret code
    game = WordleRules()

    # Create a game object with specific values: N = 4, M = 7, repetitions allowed, random secret code
    game = WordleRules(code_size=4, number_values=7, allow_repetition=True, secret=[0, 2, 5, 6])



The game object has the following methods (as every other :ref:`igamerules`):

- ``n_players() -> int``: Returns the number of players.
- ``first_position() -> WordlePosition``: Returns the first position of the game.
- ``next_position(movement: WordleMovement, position: WordlePosition) -> WordlePosition``: Returns the next position given a movement and a position.
- ``possible_movements(position: WordlePosition) -> List[WordleMovement]``: Returns the possible movements given a position.
- ``finished(position: WordlePosition) -> bool``: Returns whether the game is finished or not.
- ``score(position: WordlePosition) -> ScoreBoard``: Returns the :ref:`scoreboard` of the game.


Apart from class methods, ``WordleRules`` has the following specific methods:

- ``number_values()``: Get value (N).
- ``code_size()``: Get value (M).
- ``allow_repetition()``: Whether repetitions are allowed in the secret code.


-------
Example
-------

Let's see an example on how to create a play of Wordle:

.. code-block:: python

    from IArena.games.Wordle import WordleMovement, WordlePosition, WordleRules

    # CREATE GAME RULES
    # Create a game object with specific values: N = 4, M = 7, repetitions not allowed, random secret code
    game = WordleRules(code_size=4, number_values=7, allow_repetition=False, secret=[0, 2, 5, 6])

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
    winning_movement = WordleMovement(guess=[0, 2, 5, 6])  # The secret code
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

If you want to play the game manually, you can use the built-in :ref:`playable_player` class for Wordle: ``WordlePlayablePlayer``.
Next, we see how to create a playable game for wordle:

.. code-block:: python

    from IArena.games.Wordle import WordleMovement, WordlePosition, WordleRules
    from IArena.arena.GenericGame import GenericGame

    # PARAMETERS
    code_size = 4
    number_values = 7
    allow_repetition = False
    secret = [0, 2, 5, 6]  # Set None to use a random secret

    # Create game rules
    game = WordleRules(code_size=code_size, number_values=number_values, allow_repetition=allow_repetition, secret=secret)

    # Create Player
    player = WordlePlayablePlayer(name="Human")

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

Let's see how to create a player for Wordle that always plays in the first column available:

.. code-block:: python

    from IArena.interfaces.IPlayer import IPlayer
    from IArena.games.Wordle import WordleMovement, WordlePosition, WordleRules

    class MyAIPlayer(IPlayer):  # Create a class that inherits from IPlayer

        def play(self, position: WordlePosition) -> WordleMovement:  # Implement the play method
            rules = position.get_rules()  # Get the rules object from the position
            possible_movements = rules.possible_movements(position)  # Get the possible movements
            return next(possible_movements)  # Return the first movement available


    # TEST MY PLAYER
    my_player = MyAIPlayer()

    rules = WordleRules()  # Default game rules
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
