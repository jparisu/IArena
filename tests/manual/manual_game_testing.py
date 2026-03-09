
#####################################################################################
# Add ../../src/ to the system path to import the necessary modules
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, project_root)
#####################################################################################

from iarena.arening import ArenaFactory
from iarena.gaming.goldmine import GoldMineConfiguration, GoldMineRules
from iarena.playing import PolyvalentRandomPlayer
from iarena.visualizing import EmptyView

# Initialize configuration for a 6x6 generated map
config = GoldMineConfiguration(
    n_rows=6,
    n_cols=6,
    seed=0,
    compass_activated=True,
    proximity_activated=False,
    density_activated=False,
)

# Create rules instance
rules = GoldMineRules(config)

# Create a random player
player1 = PolyvalentRandomPlayer("random-bot", seed=4)  # Set a seed for reproducibility
players = [player1]

# Create an arena to play the game
arena = ArenaFactory.create_arena(
    rules=rules,
    view=EmptyView(),  # Modify this view to visualize the game state if desired
    players=players,
    max_turns=200,     # Set a maximum number of turns to prevent infinite loops
)

# Play the game and get the final score
scoreboard = arena.play(rules=rules, players=players)
print(f"Final score: {scoreboard.get_score(0)}")
