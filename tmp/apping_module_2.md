Read the project and [AGENTS.md](AGENTS.md) to contribute to the project.

The UI is not working. There is a problem between showing the state (position) of a current game, and connecting it with the player that must decide the move using function `play`.
We have to implement a way that there is a game loop (arena) in the application that ask the user for a movement, and then the GraphicalPlayer fill the space given in the interface to set the buttons or inputs required to decide the movement.
In case of GoldMine, this must be 4 buttons Up Down Left Right set in a cross layout, where only those available in the current position must be clickable. Also, add the cost of each movement to the button.

There are 3 states where the interface can be:

1. CONFIGURING
This is the state where the rules has not been set, and the configuration is still taken place.

2. PLAYING
This is the state where the game is being played, and the user can decide the movement.

3. REVIEWING
This is the state where the game has finished, and the user can review the game, step by step, to see how it was played.


Let's then differentiate in the interface 4 parts:

1. GAME SELECTION

This is a left menu where a game can be selected.
The way it is currently done is fine.

2. CONFIGURATION

A column in the left that shows the different configurations.
This column must be collapsible.
These are:

- General configuration: limit turns, limit score, etc.
- Game configuration to create rules
- Player configuration to select the player to play
- Controls configuration to show the buttons to control the current interface.
    - In "CONFIGURING": start, reset
    - In "PLAYING": reset
    - In "REVIEWING": play, pause, step forward, step backwards, frame ration, reset

If an autonomous player has been selected, pressing `start` will lead the state to "REVIEWING", and show the game result.
If a human player has been selected, pressing `start` will lead the state to "PLAYING", and show the buttons to decide the movement. Once the game has finished, the state will change to "REVIEWING", and show the game result.
Pressing `reset` will lead the state to "CONFIGURING", and show the configuration options again.


3. MOVEMENT

This is a right column that is collapsible, and shows movement information.

In state "REVIEWING", it shall show the movement taken by the player in the current step that is being shown.

In state "PLAYING", it shall show the movement options available for the player.
Create a generic `VisualPlayer` class that can be used for any game, this can use same logics as `TerminalPlayer`, check the number of movements, and show a button for each movement with the text of the movement on it.
Also, a game can create its custom player that implements this part of the interface when called `play` and retrieve a movement when the player interacts with it.

Under the movements, there is a collapsible panel to show the current scoreboard of the game.

4. POSITION

The central panel would show the current position of the game, and update it as the game progresses.

In state "REVIEWING", it shall show the position of the game in the current step that is being shown.

In state "PLAYING", it shall show the position of the game in real time as the game progresses.

In state "CONFIGURING", it shall show the description of the game.


To do all that, each game orchestrator have to inherit a Protocol `VisualGame` class with the following methods:

- `visual_configuration`: this create the configuration game panel, with buttons and inputs to configure the game.
- `visual_description`: this create the description of the game to be shown in the position panel when in state "CONFIGURING".
- `visual_position`: that shows the current position of the game in the position panel when in state "PLAYING" or "REVIEWING".
- `visual_movements`: that shows the movement options available for the player in the movement panel when in state "PLAYING", and the movement taken in the current step in state "REVIEWING"`.
- `visual_scoreboard`: that shows the current score of the game.

Each of this functions must be retrieve a streamlit container that will be used to show the information in its respective panel.

For example, in the case of GoldMine, the `visual_movements` will show 4 buttons in a cross layout with the cost of each movement, and only those available in the current position will be clickable. When the user clicks on one of the buttons, it will decide the movement to take in the game.
Also, int `visual_position` it will add a collapsible panel to show the secret map of the game (that the user is not supposed to see, but to simplify it can see it if click here) that shows in a matplotlib matrix the current state: the position of the player, the position of the gold, the cost of each tile and those tiles that are digged. For this, it can use `plot_square_map`.
