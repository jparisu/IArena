
from typing import List

from IArena.utils.decorators import override
from IArena.games.Wordle import WordlePosition, WordleRules, WordleMovement
from IArena.games.Mastermind import MastermindPosition, MastermindRules, MastermindMovement
from IArena.utils.RandomGenerator import RandomGenerator


class WordleOptimalPlayer_norep():

    def __init__(
            self,
            name: str = None,
            rng: RandomGenerator = RandomGenerator()):

        super().__init__(name=name)

        self.rng = rng
        self.code_size = None
        self.n_colors = None
        self.possibilities = None


    @override
    def starting_game(
            self,
            rules: WordleRules,
            player_index: int):

        self.code_size = rules.code_size()
        self.n_colors = rules.number_values()

        self.possibilities = [set(range(self.n_colors)) for _ in range(self.code_size)]


    @override
    def play(
            self,
            position: WordlePosition) -> WordleMovement:

        last_guess = position.last_guess()
        last_correct = position.last_feedback()

        # First move
        if last_guess is None:
            return self._random_guess()

        # Update possibilities
        for i, c in enumerate(last_correct):
            guess_i = last_guess[i]
            if c == WordlePosition.WordleFeedback.Correct:
                self.possibilities[i] = {guess_i}
            elif c == WordlePosition.WordleFeedback.Wrong:
                for j in range(self.code_size):
                    self.possibilities[j].discard(guess_i)
            else:
                self.possibilities[i].discard(guess_i)

        return self._random_guess()


    def _random_guess(self) -> WordleMovement:

        guess = []

        for i in range(self.code_size):
            color = self.rng.choice(self.possibilities[i])
            guess.append(color)

        return WordleMovement(guess)


class WordleOptimalPlayer_rep():

    @override
    def play(
            self,
            position: WordlePosition) -> WordleMovement:

        rules = position.get_rules()
        code_size = rules.code_size()
        n_colors = rules.number_values()
        feedback = position.feedback()

        if len(feedback) < n_colors:
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
