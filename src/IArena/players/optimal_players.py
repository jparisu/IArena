
from typing import List, Tuple

from IArena.games.NumberGuess import NumberGuessPosition, NumberGuessRules, NumberGuessMovement
from IArena.games.Wordle import WordlePosition, WordleRules, WordleMovement
from IArena.games.Mastermind import MastermindPosition, MastermindRules, MastermindMovement
from IArena.interfaces.IPlayer import IPlayer
from IArena.utils.decorators import override
from IArena.utils.RandomGenerator import RandomGenerator
from IArena.utils.containing import SortedList
from IArena.utils.excepting import ShouldNotHappenError


class NumberGuess_OptimalPlayer(IPlayer):

    def play(
            self,
            position: NumberGuessPosition) -> NumberGuessMovement:

        guesses = position.guesses()
        return NumberGuessMovement(len(guesses))



class Wordle_OptimalPlayer_norep(IPlayer):

    def __init__(
            self,
            name: str = None):

        super().__init__(name=name)

        self.code_size = None
        self.number_values = None
        self.possibilities = None


    def starting_game(
            self,
            rules: WordleRules,
            player_index: int):

        self.code_size = rules.code_size()
        self.number_values = rules.number_values()

        self.possibilities = [
            SortedList(range(self.number_values)) for _ in range(self.code_size)
        ]


    def play(
            self,
            position: WordlePosition) -> WordleMovement:

        last_guess = position.last_guess()
        last_correct = position.last_feedback()

        # First move
        if last_guess is None:
            return self._starting_all_numbers()

        # Update possibilities
        for i, c in enumerate(last_correct):
            guess_i = last_guess.guess[i]
            if c == WordlePosition.WordleFeedback.Correct:
                self.possibilities[i] = SortedList([guess_i])
                for j in range(self.code_size):
                    if j != i:
                        self.possibilities[j].remove_if_exists(guess_i)
            elif c == WordlePosition.WordleFeedback.Wrong:
                for j in range(self.code_size):
                    if guess_i in self.possibilities[j]:
                        self.possibilities[j].remove_if_exists(guess_i)
            else:
                if guess_i in self.possibilities[i]:
                    self.possibilities[i].remove_if_exists(guess_i)

        # If in first rounds, try to play all numbers
        l = len(position.guesses())
        if l < (self.number_values // self.code_size + 1):
            return self._starting_all_numbers(l)

        # If a value is unique in a position, it is correct
        for i in range(self.code_size):
            if len(self.possibilities[i]) == 1:
                val = self.possibilities[i][0]
                for j in range(self.code_size):
                    if j != i:
                        self.possibilities[j].remove_if_exists(val)

        # If one value only appears in one position, it is correct
        all_possibilities = []
        for c in range(self.number_values):
            count = 0
            index = -1
            for i in range(self.code_size):
                if c in self.possibilities[i]:
                    count += 1
                    index = i
            if count == 1:
                self.possibilities[index] = SortedList([c])


        # Else, play arbitrary valid guess
        return self._arbitrary_guess()


    def _starting_all_numbers(self, n: int = 0) -> WordleMovement:
        code_size = self.code_size
        number_values = self.number_values
        guess = []
        for i in range(code_size):
            guess.append((i + n * code_size) % number_values)
        return WordleMovement(guess)


    def _arbitrary_guess(self) -> WordleMovement:

        code_size = self.code_size
        number_values = self.number_values
        possibilities = self.possibilities

        # Calculate number of possibilities for space
        n_possibilities = [len(p) for p in possibilities]

        # Move from the most constrained space
        indexes = [0] * code_size

        numbers_selected = set()
        guess = []

        index = 0

        while index < code_size:

            p = possibilities[index][indexes[index]]

            if p not in numbers_selected:
                numbers_selected.add(p)
                guess.append(p)
                index += 1

            else:
                indexes[index] += 1
                while indexes[index] >= n_possibilities[index]:
                    indexes[index] = 0
                    index -= 1

                    x = guess.pop()
                    numbers_selected.remove(x)

                    indexes[index] += 1

        return WordleMovement(guess)


class Wordle_NonOptimalPlayer_norep(IPlayer):

    def __init__(
            self,
            name: str = None,
            rng: RandomGenerator = RandomGenerator()):

        super().__init__(name=name)

        self.rng = rng
        self.code_size = None
        self.number_values = None
        self.possibilities = None


    def starting_game(
            self,
            rules: WordleRules,
            player_index: int):

        self.code_size = rules.code_size()
        self.number_values = rules.number_values()

        self.possibilities = [list(range(self.number_values)) for _ in range(self.code_size)]

        # Shuffle possibilities
        for p in self.possibilities:
            self.rng.shuffle(p)


    def play(
            self,
            position: WordlePosition) -> WordleMovement:

        last_guess = position.last_guess()
        last_correct = position.last_feedback()

        # First move
        if last_guess is None:
            return self._arbitrary_guess()

        # Update possibilities
        for i, c in enumerate(last_correct):
            guess_i = last_guess.guess[i]
            if c == WordlePosition.WordleFeedback.Correct:
                self.possibilities[i] = [guess_i]
                for j in range(self.code_size):
                    if j != i:
                        if guess_i in self.possibilities[j]:
                            self.possibilities[j].remove(guess_i)
            elif c == WordlePosition.WordleFeedback.Wrong:
                for j in range(self.code_size):
                    if guess_i in self.possibilities[j]:
                        self.possibilities[j].remove(guess_i)
            else:
                if guess_i in self.possibilities[i]:
                    self.possibilities[i].remove(guess_i)

        return self._arbitrary_guess()


    def _arbitrary_guess(self) -> WordleMovement:

        # Calculate number of possibilities for space
        n_possibilities = [len(p) for p in self.possibilities]

        # Move from the most constrained space
        indexes = [0] * self.code_size

        while True:

            guess = [p[i] for i, p in zip(indexes,self.possibilities)]
            while not self._no_rep_valid_guess(guess):
                indexes[-1] += 1
                i = -1
                while indexes[i] >= n_possibilities[i]:
                    indexes[i] = 0
                    i -= 1
                    indexes[i] += 1
                guess = [p[i] for i, p in zip(indexes,self.possibilities)]

            else:
                return WordleMovement(guess)


    def _no_rep_valid_guess(self, guess) -> bool:
        return len(guess) == len(set(guess))


class Wordle_OptimalPlayer_rep(IPlayer):

    @override
    def play(
            self,
            position: WordlePosition) -> WordleMovement:

        rules = position.get_rules()
        code_size = rules.code_size()
        number_values = rules.number_values()
        feedback = position.feedback()

        if len(feedback) < number_values:
            return self._all_n_guess(code_size, len(feedback))
        else:
            return self._correct_guess(feedback)

    @staticmethod
    def _all_n_guess(size: int, n: int) -> WordleMovement:
        guess = [n] * size
        return WordleMovement(guess)

    @staticmethod
    def _correct_guess(all_feedback: List[List[WordlePosition.WordleFeedback]]) -> WordleMovement:
        guess = [0] * len(all_feedback[0])
        for i, corr in enumerate(all_feedback):
            for j, c in enumerate(corr):
                if c == WordlePosition.WordleFeedback.Correct:
                    guess[j] = i
        return WordleMovement(guess)


class Mastermind_NonOptimalPlayer_rep(IPlayer):

    def __init__(
            self,
            name: str = None):

        super().__init__(name=name)

        self.code_size = None
        self.number_values = None
        self.number_per_value = None
        self.fix_positions = None


    def starting_game(
            self,
            rules: MastermindRules,
            player_index: int):

        self.code_size = rules.code_size()
        self.number_values = rules.number_values()

        self.number_per_value = [0] * self.number_values
        self.fix_positions = [0] * self.code_size
        self.ready = False

        # STATUS:
        # 0: Strategy to move
        # 1: Strategy to update
        # 2: Strategy internal value
        self.status = [0, 0, 0]


    @override
    def play(
            self,
            position: MastermindPosition) -> MastermindMovement:

        # Status update
        if self.status[1] == 0:
            self.status[1] = 1
        elif self.status[1] == 1:
            self._strategy1_update(position)
        elif self.status[1] == 2:
            self._strategy2_update(position)

        # Next move
        if self.status[0] == 0:
            return self._strategy1_move(position)

        elif self.status[0] == 1:
            return self._strategy2_move(position)

        else:
            return self._strategy3_move(position)



    """
    N: code_size
    M: number_values

    STRATEGY 1:
    The first M turns, play all 0, then all 1, ..., all M-1.

    STRATEGY 2:
    The following M*N turns, play all values i and j (i != j) in all positions

    STRATEGY 3:
    When all values are found, and all positions are fixed, play the correct guess.
    """

    def _strategy1_update(self, position: MastermindPosition):
        feedback = position.last_feedback()
        self.number_per_value[self.status[2]] = feedback.correct

        # UPDATE STATUS
        if self.status[2] >= self.number_values - 1:
            # If finished strategy 1
            self.status = [1, 2, 0]

        else:
            # Update next move
            self.status[2] += 1

    def _strategy1_move(self, position: MastermindPosition) -> MastermindMovement:
        return self._all_n_guess(self.code_size, self.status[2])


    def _strategy2_update(self, position: MastermindPosition):
        last_guess = position.last_guess()
        last_feedback = position.last_feedback()

        # Get values i and j for last guess
        l = self.status[2]
        i = l // self.code_size
        i_index = l % self.code_size
        j = (i + 1) % self.number_values

        # Update fixed positions if required
        n_j_total_correct = self.number_per_value[j]
        correct = last_feedback.correct

        if correct >= n_j_total_correct:
            # All j are found. Do nothing
            pass

        else:
            # The gap in i_index is a j
            self.fix_positions[i_index] = j


        # Update status
        if self.status[2] >= self.number_values * self.code_size - 1:
            # If finished strategy 2
            self.status = [2, 2, 0]

        else:
            # Update next move
            self.status[2] += 1


    def _strategy2_move(self, position: MastermindPosition) -> MastermindMovement:

        l = self.status[2]

        i = l // self.code_size
        i_index = l % self.code_size
        j = (i + 1) % self.number_values

        guess = [j] * self.code_size
        guess[i_index] = i

        return MastermindMovement(guess=guess)


    def _strategy3_move(self, position: MastermindPosition) -> MastermindMovement:
        return MastermindMovement(guess=list(self.fix_positions))


    @staticmethod
    def _all_n_guess(size: int, n: int) -> MastermindMovement:
        guess = [n] * size
        return MastermindMovement(guess)




class Mastermind_OptimalPlayer_rep(IPlayer):

    def __init__(
            self,
            name: str = None):

        super().__init__(name=name)

        self.code_size = None
        self.number_values = None
        self.number_per_value = None
        self.fix_positions = None
        self.status = None
        self.positions_to_try = None


    def starting_game(
            self,
            rules: MastermindRules,
            player_index: int):

        self.code_size = rules.code_size()
        self.number_values = rules.number_values()

        self.number_per_value = [-1] * self.number_values
        self.fix_positions = [-1] * self.code_size
        self.positions_to_try = [list(range(self.code_size)) for _ in range(self.number_values)]
        self.ready = False

        # STATUS:
        # 0: Strategy to set all values equal
        # 1: Strategy to set all values less one
        # 2: Strategy to set correct guess
        self.status = -1


    @override
    def play(
            self,
            position: MastermindPosition) -> MastermindMovement:

        # print(f"DEBUG: Strategy {self.status}")
        # print(f"  NxV: {self.number_per_value}")
        # print(f"  Fix: {self.fix_positions}")
        # print(f"  Try: {self.positions_to_try}")
        # print(f"  Pos:\n{position}")
        # print()

        # Starting
        if self.status == -1:
            self.status = 0
            return self._strategy_0_first_move()

        # Status 0
        elif self.status == 0:
            return self._strategy_0(position)

        # Status 1
        elif self.status == 1:
            return self._strategy1(position)

        raise ShouldNotHappenError(f"Mastermind_OptimalPlayer_rep: Invalid status {self.status}.\n Position: {position}")

    ##########################
    # STRATEGY 0
    """
    In this strategy, we try to find the number of occurrences of each value by setting
    all the code to the same value
    """

    def _strategy_0_next_non_tried(self) -> int:
        """Next value to try in strategy 0 where we still do not know its number of occurrences"""
        for i in range(self.number_values):
            if self.number_per_value[i] == -1:
                return i
        return -1

    def _strategy_0_should_stop(self) -> bool:
        """Check if we have found the number of occurrences of all values"""
        s = 0
        for i in range(self.number_values):
            if self.number_per_value[i] != -1:
                s += self.number_per_value[i]
        return s == self.code_size

    def _strategy_0_only_one_remaining(self) -> bool:
        """We can deduce the number of occurrences of the last remaining value"""
        s = 0
        for i in range(self.number_values):
            if self.number_per_value[i] != -1:
                s += self.number_per_value[i]
        self.number_per_value[-1] = self.code_size - s
        return self._strategy_0_pass_to_1()

    def _strategy_0_update(self, position: MastermindPosition):
        last_guess = position.last_guess()
        last_feedback = position.last_feedback()

        val = last_guess.guess[0]
        self.number_per_value[val] = last_feedback.correct

    def _strategy_0_move(self, position: MastermindPosition) -> MastermindMovement:
        val = self._strategy_0_next_non_tried()
        if val == self.number_values - 1:
            return self._strategy_0_only_one_remaining()
        return self._strategy_0_all_n_guess(val)

    def _strategy_0_first_move(self) -> MastermindMovement:
        return self._strategy_0_all_n_guess(0)

    def _strategy_0(self, position: MastermindPosition) -> MastermindMovement:
        self._strategy_0_update(position)
        if self._strategy_0_should_stop():
            return self._strategy_0_pass_to_1()
        else:
            return self._strategy_0_move(position)

    def _strategy_0_all_n_guess(self, n: int) -> MastermindMovement:
        guess = [n] * self.code_size
        return MastermindMovement(guess)

    def _strategy_0_pass_to_1(self) -> MastermindMovement:
        self.status = 1
        return self._strategy1_first_move()

    ##########################
    # STRATEGY 1
    """
    In this strategy, we try to fix the positions of the values we found in strategy 0
    We set all positions to a known value A except position X, which we set to another known value B
    Being Ca number of occurrences of value A, and Cb number of occurrences of value B,
        1. correct == Ca + 1 -> position of B is fixed in X
        2. correct == Ca and misplaced == 1 -> position of B is not in X
        3. correct < Ca -> position of A is in X, position of B is not in X
    """

    def _strategy1_first_move(self) -> MastermindMovement:
        """
        Starting strategy 1: set possibilities and check if only one color.
        Then, do first move.
        """
        if self._strategy1_only_one_color():
            return self._strategy_1_pass_to_2()
        self._strategy1_set_possibilities()

        return self._strategy1_move()


    def _strategy1_set_possibilities(self):
        """Set possible positions for each value"""
        for i, x in enumerate(self.number_per_value):
            if x == 0:
                self.positions_to_try[i] = []


    def _strategy1_only_one_color(self) -> bool:
        """Check if there is only one color to set"""
        for i, x in enumerate(self.number_per_value):
            if x == self.code_size:
                self.fix_positions = [i] * self.code_size
                return True
        return False


    def _strategy1_should_stop(self) -> bool:
        """Check if all positions are fixed"""
        return all(p != -1 for p in self.fix_positions)


    def _strategy1_select_colors(self) -> Tuple[int, int, int]:
        """Select colors A and B and position X for strategy 1 move"""
        # Find first position without fixed value
        x = -1
        for i in range(self.code_size):
            if self.fix_positions[i] == -1:
                x = i
                break

        # If there is not non-fixed position, move to strategy 2
        if x == -1:
            return -1, -1, -1

        # Find a color A that is not fixed in X
        a = -1
        for i in range(self.number_values):
            positions = self.positions_to_try[i]
            if len(positions) > 0 and x in positions:
                a = i
                break

        # There must always be a color A that can go in X
        if a == -1:
            raise ShouldNotHappenError("Mastermind_OptimalPlayer_rep: Could not select color A for strategy 1")

        # Find a color B different from A that can go in X
        b = -1
        for i in range(a+1, self.number_values):
            positions = self.positions_to_try[i]
            if len(positions) > 0 and x in positions:
                b = i
                break

        # It may happen that only one color remains for X
        if b == -1:
            self._strategy1_set_fixed(a, x)
            return self._strategy1_select_colors()

        return a, b, x


    def _strategy1_move(self) -> MastermindMovement:
        a, b, x = self._strategy1_select_colors()

        # If no more movements
        if x == -1:
            return self._strategy_1_pass_to_2()

        guess = [a] * self.code_size
        guess[x] = b
        return MastermindMovement(guess=guess)

    def _strategy1_update(self, position: MastermindPosition):
        last_guess = position.last_guess()
        last_feedback = position.last_feedback()
        corrects = last_feedback.correct
        misplaced = last_feedback.misplaced

        # Get a, b, x
        a, b, x = self._strategy1_select_colors()

        # print(f"DEBUG: colors selected: {a}, {b}, {x}")

        # Update fixed positions if required
        # Case 1: position x is b
        if corrects == self.number_per_value[a] + 1:
            self._strategy1_set_fixed(b, x)

        elif corrects == self.number_per_value[a] and misplaced == 1:
            # Case 2: position x is not b
            self._strategy1_remove_possibility(b, x)
            self._strategy1_remove_possibility(a, x)

        else:
            # Case 3: position x is a
            self._strategy1_set_fixed(a, x)


    def _strategy1_set_fixed(self, color: int, position: int):

        # print(f"DEBUG: Setting fixed color {color} in position {position}")

        if self.fix_positions[position] != -1:
            raise ShouldNotHappenError(f"Mastermind_OptimalPlayer_rep: Trying to fix {color} in {position} in an already fixed position with {self.fix_positions[position]}.")

        self.fix_positions[position] = color

        # Remove this position from every position to try
        for i in range(self.number_values):
            if position in self.positions_to_try[i]:
                self._strategy1_remove_possibility(i, position)

    def _strategy1_remove_possibility(self, color: int, position: int):

        # print(f"DEBUG: Removing possibility color {color} in position {position}")

        if position in self.positions_to_try[color]:
            self.positions_to_try[color].remove(position)

        while True:
            # Check how many values of this color are fixed
            n_fixed = sum(1 for p in self.fix_positions if p == color)
            n_per_fix = self.number_per_value[color] - n_fixed

            # If the values fixed plus the remaining possibilities equal the total number of occurrences,
            # then fix all remaining possibilities
            if n_per_fix > 0 and n_fixed + len(self.positions_to_try[color]) == self.number_per_value[color]:
                self._strategy1_set_fixed(color, self.positions_to_try[color][0])
            else:
                break


    def _strategy1(self, position: MastermindPosition) -> MastermindMovement:
        try:

            self._strategy1_update(position)
            if self._strategy1_should_stop():
                return self._strategy_1_pass_to_2()
            else:
                return self._strategy1_move()
        except ShouldNotHappenError as e:
            raise ShouldNotHappenError(f"Mastermind_OptimalPlayer_rep: Error in strategy 1.\n Position: {position}") from e

    def _strategy_1_pass_to_2(self) -> MastermindMovement:
        self.status = 2
        return self._strategy2_first_move()

    ##########################
    # STRATEGY 2
    # We already know all the fixed positions, just send the movement

    def _strategy2_first_move(self) -> MastermindMovement:
        return MastermindMovement(guess=list(self.fix_positions))
