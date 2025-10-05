
from typing import List

from IArena.utils.decorators import override
from IArena.games.NumberGuess import NumberGuessPosition, NumberGuessRules, NumberGuessMovement
from IArena.games.Wordle import WordlePosition, WordleRules, WordleMovement
from IArena.games.Mastermind import MastermindPosition, MastermindRules, MastermindMovement
from IArena.utils.RandomGenerator import RandomGenerator
from IArena.interfaces.IPlayer import IPlayer


class NumberGuessOptimalPlayer_norep(IPlayer):

    def play(
            self,
            position: NumberGuessPosition) -> NumberGuessMovement:

        guesses = position.guesses()
        return NumberGuessMovement(len(guesses))



class WordleOptimalPlayer_norep(IPlayer):

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


class WordleOptimalPlayer_rep():

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
