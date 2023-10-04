
"""PlayerIndex class represents the index of a player."""
class PlayerIndex(int):
    FirstPlayer = 0

def two_player_game_change_player(n: PlayerIndex):
    """Get a player different to n in a 2 players game."""
    return PlayerIndex(not n)
