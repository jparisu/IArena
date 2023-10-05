import time

import IArena.tournaments.PlayableGame
import IArena.tournaments.GenericGame
import IArena.games.Hanoi
import IArena.games.FieldWalk
import IArena.games.BlindWalk
import IArena.players.players

# class MyRandPlayer(IArena.players.players.RandomPlayer):

#     def play(
#             self,
#             position):
#         time.sleep(1)
#         return IArena.players.players.RandomPlayer.play(self, position)

# rules = IArena.games.Hanoi.HanoiRules()
# game = IArena.tournaments.GenericGame.BroadcastGame(rules, [MyRandPlayer(rules, 0)])
# print(f"You got it in : {game.play()} movements")

rules = IArena.games.BlindWalk.BlindWalkRules()
# print(rules.__map)

rules = IArena.games.FieldWalk.FieldWalkRules()
print(rules.get_map())
game = IArena.tournaments.PlayableGame.PlayableGame(rules)
print(f"You got it in : {game.play()} movements")
