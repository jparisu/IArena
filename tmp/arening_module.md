Let's start implementing module `arening`,
This module will implement arenas, this is, loop games.

The generic one just receives a game rules and a list of players. The position of each player will be their index.
With that, create a loop of positions, and ask the player which turn is next to select a movement, by method "play".

Then, I want to create specific limitations or behaviors for different arenas, so we may want to use protocols or patterns to create specific behaviors, an later on mix them in a specific arena by a factory.

- Time limitation per turn: if a player takes more than a certain time to select a movement, they will lose the game.

- Time limitation for the whole game: if a game takes more than a certain time to finish, it ends with bad results for all players.

- Turn limitation: if a game takes more than a certain number of turns, it ends with bad results for all players.

- Score limitation: if a game exceeds a certain minimum score for any player, it ends.

- Store information: store the information of the game, such as the positions and the movements. This will be helpful to afterwards analyze the game, and also to be able to replay it.

- TerminalArena: an arena that shows the game in the terminal, and allows the user to play by inputting the movements. This will be useful for testing and debugging purposes, as well as for playing the game in a non-graphical way. It will require a game where position and movements implement the correct protocols for string representations. It should also show the rules at the beginning, so game rules should also implement a protocol for that.
