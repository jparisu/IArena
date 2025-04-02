
.. _glossary:

########
Glossary
########

.. glossary::

    Arena
        A class that represents the game flow. Uses one GameRule and several players to play a game, returning the final score.

    GameRule
        A class that defines the rules of a game. It contains methods to help creating the game flow.

    Movement
        A class that represents a movement in a game. Along with GameRules, generates new Positions given a source one.

    Player
        A class that represents a player in a game. It contains the method to return a movement given a position.

    PlayerIndex
        ``int`` variable that represents the index of a player in a game.

    Position
        A class that represents a specific state of a game. Along with the GameRules, it defines the game.

    Score
        ``float`` variable that indicates how good the final game went.
        After finishing any game, you get a ``ScoreBoard`` that holds the score for each player.

    ScoreBoard
        A class that represents a list of the scores of a terminated game. Each player has its own score.
