#####################################################################################
# PRACTICA 0

from IArena.games.Connect4 import Connect4Rules, Connect4Movement, Connect4Position
from IArena.interfaces.IPlayer import IPlayer

# Define player class
class MyPlayer(IPlayer):

    def play(
            self,
            position: Connect4Position) -> Connect4Movement:
        # IMPLEMENT YOUR CODE HERE
        # This is a simple example that plays a random move
        rules = position.get_rules()
        moves = rules.possible_movements(position)
        my_player = position.next_player()

        # Check if any of the current moves win:
        final_move_index = -1
        for i, m in enumerate(moves):
            next_position = rules.next_position(m, position)
            if rules.finished(next_position):
                final_move_index = i
                break

        return moves[final_move_index]


# Create player instance (can add ctor parameters if needed)
my_player = MyPlayer(name="Student")


#####################################################################################


#####################################################################################
# PRACTICA 1

from IArena.games.Connect4 import Connect4Rules, Connect4Movement, Connect4Position
from IArena.interfaces.IPlayer import IPlayer

def minimax(position, max_player_turn, max_player):
    rules = position.get_rules()

    if rules.finished(position):
        s = rules.score(position)
        return s.get_score(max_player)

    movements = rules.possible_movements(position)

    if max_player_turn:
        score = -1
        for move in movements:
            next_position = rules.next_position(move, position)
            next_score = minimax(next_position, not max_player_turn, max_player)
            score = max(score, next_score)
            if score == 1:
                return score
        return score
    else:
        score = 1
        for move in movements:
            next_position = rules.next_position(move, position)
            next_score = minimax(next_position, not max_player_turn, max_player)
            score = min(score, next_score)
            if score == -1:
                return score
        return score

# Define player class
class MyPlayer(IPlayer):

    def play(
            self,
            position: Connect4Position) -> Connect4Movement:
        scores = []
        movements = position.get_rules().possible_movements(position)
        for move in movements:
            next_position = position.get_rules().next_position(move, position)
            scores.append(minimax(next_position, False, position.next_player()))

        return movements[scores.index(max(scores))]


# Create player instance (can add ctor parameters if needed)
my_player = MyPlayer(name="Student")

#############
# Result 2
# 1: wins first [0]
# 2: wins first [0]
# 3: tie
# 4: wins first [0]
# 5: tie


#####################################################################################


#####################################################################################
# PRACTICA 2

from IArena.games.Connect4 import Connect4Rules, Connect4Movement, Connect4Position
from IArena.interfaces.IPlayer import IPlayer

def minimax(position, max_player_turn, max_player, depth=3):
    rules = position.get_rules()

    if rules.finished(position):
        s = rules.score(position)
        return s.get_score(max_player)

    elif depth == 0:
        return 0

    movements = rules.possible_movements(position)
    scores = []
    for move in movements:
        next_position = rules.next_position(move, position)
        next_score = minimax(next_position, not max_player_turn, max_player, depth=depth-1)
        scores.append(next_score)

    if max_player_turn:
        return max(scores)
    else:
        return min(scores)

# Define player class
class MyPlayer(IPlayer):

    def play(
            self,
            position: Connect4Position) -> Connect4Movement:
        scores = []
        movements = position.get_rules().possible_movements(position)
        for move in movements:
            next_position = position.get_rules().next_position(move, position)
            scores.append(minimax(next_position, False, position.next_player()))

        return movements[scores.index(max(scores))]


# Create player instance (can add ctor parameters if needed)
my_player = MyPlayer(name="Student")

#####################################################################################


#####################################################################################
# PRACTICA 3

from IArena.games.Nim import NimRules, NimMovement, NimPosition
from IArena.interfaces.IPlayer import IPlayer

# Define player class
class MyPlayer(IPlayer):

    def xor(self, position):
        xor = 0
        for line in position.lines:
            xor ^= line
        return xor


    def play(
            self,
            position: NimPosition) -> NimMovement:
        movements = position.get_rules().possible_movements(position)
        best_movement = movements[0]
        for move in movements:
            next_position = position.get_rules().next_position(move, position)
            if self.xor(position) == 0:
                best_movement = move
                break

        return best_movement


# Create player instance (can add ctor parameters if needed)
my_player = MyPlayer(name="Student")

#####################################################################################
