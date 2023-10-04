
import IArena.tournaments.PlayableGame
import IArena.tournaments.GenericGame
import IArena.games.Hanoi
import IArena.players.players

# Choose the game to play
rules = IArena.games.Hanoi.HanoiRules()

game = IArena.tournaments.PlayableGame.PlayableGame(rules)
print(f"You got it in : {game.play()} movements")
