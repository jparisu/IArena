
from typing import List

from IArena.games.NumberGuess import NumberGuessPosition, NumberGuessRules, NumberGuessMovement
from IArena.games.Wordle import WordlePosition, WordleRules, WordleMovement
from IArena.games.Mastermind import MastermindPosition, MastermindRules, MastermindMovement
from IArena.interfaces.IPlayer import IPlayer
from IArena.utils.decorators import override
from IArena.utils.RandomGenerator import RandomGenerator
from IArena.utils.containing import SortedList


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


class Mastermind_OptimalPlayer_rep(IPlayer):

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
            rules: WordleRules,
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
            position: WordlePosition) -> WordleMovement:

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

    def _strategy1_update(self, position: WordlePosition):
        feedback = position.last_feedback()
        self.number_per_value[self.status[2]] = feedback.correct

        # UPDATE STATUS
        if self.status[2] >= self.number_values - 1:
            # If finished strategy 1
            self.status = [1, 2, 0]

        else:
            # Update next move
            self.status[2] += 1

    def _strategy1_move(self, position: WordlePosition) -> WordleMovement:
        return self._all_n_guess(self.code_size, self.status[2])


    def _strategy2_update(self, position: WordlePosition):
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


    def _strategy2_move(self, position: WordlePosition) -> WordleMovement:

        l = self.status[2]

        i = l // self.code_size
        i_index = l % self.code_size
        j = (i + 1) % self.number_values

        guess = [j] * self.code_size
        guess[i_index] = i

        return MastermindMovement(guess=guess)


    def _strategy3_move(self, position: WordlePosition) -> WordleMovement:
        return MastermindMovement(guess=list(self.fix_positions))


    @staticmethod
    def _all_n_guess(size: int, n: int) -> WordleMovement:
        guess = [n] * size
        return WordleMovement(guess)
