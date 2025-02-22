
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

    Position
        A class that represents a specific state of a game. Along with the GameRules, it defines the game.

    Score
        A class that represents the score of a terminated game. Each player has its own score.
