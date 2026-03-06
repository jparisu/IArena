Let's start implementing module `apping`,
In this module we will have 2 parts:

1. Generic classes and functions to be able to play a game interactively in streamlit. Those must be generic so any game can implement their own way of playing.

In this case we want to create a 1 player optimization game.
Thus, we will create generic classes and functions to play this kind of games.

The main window will be divided in a left column for configuration of the game, player selection, and the buttons to reset, start, etc.

Players could be to upload a .py file that plays. In this case, the whole game will be played, and then shown with a progression bar where the user can play, pause, step forward and backwards.

If not, use a generic player that will be given by the specific game.
Also, allow for generic players, such as random or so.

Then, the central panel should show the information required for the game. For example, in case of GoldMine game, it should only show the cost so far, and the possible current movements, along with their cost. Also, if compass activa, it shall show the compass information.

Some games may allow a secret information, as in GoldMine the actual matrix of the map.
Add a colapsable section for this information.


With this, GoldMine game should be able to implement the graphical streamlit app reusing this generic elements.


2. Streamlit app that holds an index for different games, and that when a game is selected, move to the page of the game.
This will be the main page of the app, where we will have a sidebar with the list of games, and when we select one, it will show the game page.

Each game generated must be only a sub-page inside this main page.
