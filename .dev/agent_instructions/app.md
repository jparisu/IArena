It's time to create the first visual application for our project `iarena`.
The design is in [skeleton.py](.dev/design/skeleton.py) .

We need a new application that runs an streamlit application that allows to play any game in the `iarena` environment. We will call this application `StreamlitApplication`.
This will be divided in many components:

# Interface

## Left Menu

A collapsible sidebar to select the game. Use `GameGovernor` to get the possible games that implement a Streamlit View.

## Left Sidebar - Configuration

A section to select the configuration of the game.
This is divided in some tabs:

1. Player selection: A section to select the players. This could be done by selecting from the list of possible players that comes from `Game` class of the specific game. Only streamlit players or automatic players can be used.
2. Arena configuration: Set a maximum of movements
3. Game configuration: Use the streamlit app inherited class specific for the game to create the configuration. Or use a configuration file in .yaml format.
4. Controls: Init, Restart. In REVIEWING state, play, pause, step forward, step backward.

## Right Sidebar - Movements and score

Show the possible movements by the implementation of the specific game class to interact with the interface.
The movements, may be buttons, text input, etc.
The specific StreamlitPlayer for the specific game must be able to retrieve a movement from a streamlit state.

Under that, show the current score for the current position.

If in REVIEWING state, show the movement selected, instead of the possible movements, and the score for that position.

## Main Panel

Show the current position of the game.
This is done by the implementation of the specific game class to interact with the interface.

## Bottom - Steps

Use a slider to move across the positions and movements stored in the arena.
If not in the last step, the interface moves to REVIEWING state, not allowing user interaction until the last step is reached.




# Behavior

There are several states for the application:

1. SELECTION: Select a game. While not selected, show the first game in the list of possible games.
2. CONFIGURATION: While not clicked `Init` or `Restart`, the game has not started. In this state, the user can select the players, the configuration of the arena and the game configuration.
3. PLAYING: Once the game is initialized, the user can interact with the game by making movements. The game will update the position and the score accordingly. The user can also restart the game at any time, which will reset the state to SELECTION.
4. REVIEWING: After finishing a game, or if the player is automatic, there will be


# STEPS

1. Check the current state of the library and see if we have the necessary components to implement this application. If so, ask before starting to implement.
2.
3. Implement the application step by step, starting with the basic structure and then adding the functionality for each step of the behavior.
. Make sure the application runs a simple game: Hanoi with default configuration and a random player
4. Improve to-text functions of the app and the games to make the terminal view more user-friendly and informative.
