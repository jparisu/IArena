
import copy
from typing import Iterator, List
from enum import Enum
import itertools

from IArena.grader.RulesGenerator import IRulesGenerator
from IArena.interfaces.IPlayer import IPlayer
from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.interfaces.ScoreBoard import ScoreBoard
from IArena.utils.decorators import override
from IArena.utils.RandomGenerator import RandomGenerator

"""
This game represents the Wordle game with exact tips.
In this game there is a pattern hidden and the player must guess it.
The pattern is a list of N numbers from 0 to M-1.
The player makes guesses and the game tells how many numbers are correct and in the right position.
The game ends when the player guesses the pattern.

NOTE:
1. In this implementation, the game is played by one player, and the pattern is not known.
2. The numbers (letters in actual game) could or nor be repeated depending on the configuration.
3. The game tells for each guess exactly which numbers are correct and in the right position.
"""

class WordleMovement(IMovement):
    """
    Represents the movement of the player in the game by guessing the pattern.
    It is a list of N numbers with numbers from 0 to M-1.

    Attributes:
        guess: The guess of the player.
    """

    def __init__(
            self,
            guess: List[int]):
        self.guess = guess

    def __eq__(
            self,
            other: "WordleMovement"):
        return self.guess == other.guess

    def __str__(self):
        return f'{self.guess}'


class WordlePosition(IPosition):
    """
    TODO
    """

    class WordleFeedback (Enum):
        """
        Represents the feedback one number in one guess.
        """
        Wrong = 0
        Misplaced = 1
        Correct = 2

    def __init__(
            self,
            rules: "WordleRules",
            guesses: List[WordleMovement],
            feedback: List[List[WordleFeedback]]):
        super().__init__(rules)
        self._guesses = guesses
        self._feedback = feedback

    @override
    def next_player(
            self) -> PlayerIndex:
        return PlayerIndex.FirstPlayer

    def __eq__(
            self,
            other: "WordlePosition"):
        return self._guesses == other._guesses and self._feedback == other._feedback

    def __str__(self):

        if len(self._guesses) == 0:
            return "<EMPTY POSITION>\n"

        # Print each guess in a line together with the feedback
        return "\n".join([f'{self._guesses[i]} : {[x.name for x in self._feedback[i]]}' for i in range(len(self._guesses))]) + "\n"

    def guesses(self) -> List[WordleMovement]:
        return copy.deepcopy(self._guesses)

    def feedback(self) -> List[List[WordleFeedback]]:
        return copy.deepcopy(self._feedback)

    def last_guess(self) -> WordleMovement:
        if len(self._guesses) == 0:
            return None
        return copy.deepcopy(self._guesses[-1])

    def last_feedback(self) -> List[WordleFeedback]:
        if len(self._feedback) == 0:
            return None
        return copy.deepcopy(self._feedback[-1])

    def code_size(self) -> int:
        return self.get_rules().code_size()

    def number_values(self) -> int:
        return self.get_rules().number_values()

    def allow_repetition(self) -> bool:
        return self.get_rules().allow_repetition()


class WordleRules(IGameRules):

    DefaultCodeSize = 5
    DefaultNumberValues = 8

    @staticmethod
    def random_secret(
                code_size: int,
                number_values: int,
                rng: RandomGenerator,
                allow_repetition: bool = True) -> List[int]:
        if not allow_repetition and code_size > number_values:
            raise ValueError("n must be less than or equal to m when allow_repetition is False")
        if allow_repetition:
            return [rng.randint(number_values) for _ in range(code_size)]
        else:
            possible_letters = set(range(number_values))
            letters = []
            for _ in range(code_size):
                letter = rng.choice(list(possible_letters))
                letters.append(letter)
                possible_letters.remove(letter)
            return letters


    def __init__(
            self,
            code_size: int = DefaultCodeSize,
            number_values: int = DefaultNumberValues,
            secret: List[int] = None,
            allow_repetition: bool = True):
        """
        Construct a secret code of size n with numbers from 0 to m-1.

        If a secret is not provided, a new one is generated using the seed provided.
        n and m must be provided.

        If a secret is provided, it is used instead of generating a new one.
        m must be always provided.

        Args:
            code_size: Size of the code.
            number_values: Number of different values (from 0 to m-1).
            secret: Seed for the random generator.
            allow_repetition: The secret code.
        """

        if secret is None:
            secret = WordleRules.random_secret(
                code_size=code_size,
                number_values=number_values,
                rng=RandomGenerator(),
                allow_repetition=allow_repetition,
            )

        self.m = number_values
        self.n = code_size
        if len(secret) != code_size or any(x < 0 or x >= number_values for x in secret):
            raise ValueError("Secret must be of size n and with numbers from 0 to m-1")
        if not allow_repetition and len(set(secret)) != code_size:
            raise ValueError("Secret must not have repetitions when allow_repetition is False")
        self.__secret = secret
        self.allow_repetition_ = allow_repetition

    def number_values(self) -> int:
        return self.m

    def code_size(self) -> int:
        return self.n

    def allow_repetition(self) -> bool:
        return self.allow_repetition_

    @override
    def n_players(self) -> int:
        return 1

    @override
    def first_position(self) -> WordlePosition:
        return WordlePosition(self, [], [])

    @override
    def next_position(
            self,
            movement: WordleMovement,
            position: WordlePosition) -> WordlePosition:
        guesses = position.guesses() + [movement]

        # Check if the movement is valid
        if len(movement.guess) != self.n or any(x < 0 or x >= self.m for x in movement.guess):
            raise ValueError(f"Movement must be of size {self.n} and with numbers from 0 to {self.m-1}")
        if not self.allow_repetition_ and len(set(movement.guess)) != self.n:
            raise ValueError("Movement must not have repetitions when allow_repetition is False")

        # Calculate the feedback of the new guess
        feedback = [WordlePosition.WordleFeedback.Wrong for _ in range(self.n)]
        already_placed = [False for _ in range(self.n)]
        possible_misplaced = []
        for i in range(self.n):
            if movement.guess[i] == self.__secret[i]:
                feedback[i] = WordlePosition.WordleFeedback.Correct
                already_placed[i] = True
            elif movement.guess[i] in self.__secret:
                possible_misplaced.append(i)

        for i in possible_misplaced:
            # Check if such number is in secret in a position that has already not being checked
            for j in range(self.n):
                if not already_placed[j] and movement.guess[i] == self.__secret[j]:
                    already_placed[j] = True
                    feedback[i] = WordlePosition.WordleFeedback.Misplaced
                    break

        new_feedback = copy.deepcopy(position.feedback())
        new_feedback.append(feedback)

        return WordlePosition(self, guesses, new_feedback)

    @override
    def possible_movements(
            self,
            position: WordlePosition) -> Iterator[WordleMovement]:

        if self.allow_repetition_:
            # Every combination of n numbers from 0 to m-1 using itertools
            for x in itertools.product(range(self.m), repeat=self.n):
                yield WordleMovement(guess=list(x))

        else:
            # Every permutation of n numbers from 0 to m-1 using itertools
            for x in itertools.permutations(range(self.m), self.n):
                yield WordleMovement(guess=list(x))

    @override
    def finished(
            self,
            position: WordlePosition) -> bool:
        # Game is finished if the last guess is equal the hidden secret
        if len(position.guesses()) == 0:
            return False
        return position.guesses()[-1].guess == self.__secret

    @override
    def score(
            self,
            position: WordlePosition) -> ScoreBoard:
        s = ScoreBoard()
        s.define_score(PlayerIndex.FirstPlayer, -len(position.guesses()))
        return s



class WordlePlayablePlayer(IPlayer):

    SeparatorN = 40

    @override
    def play(
            self,
            position: IPosition) -> IMovement:

        code_size = position.get_rules().code_size()
        number_values = position.get_rules().number_values()

        print ("=" * WordlePlayablePlayer.SeparatorN)
        print (position)
        print ("-" * WordlePlayablePlayer.SeparatorN)
        repetitions_text = "with repetition" if position.get_rules().allow_repetition() else "without repetition"
        print (f"Values: {list(range(number_values))}  ({repetitions_text})")

        letters = []

        while True:
            print ("-" * WordlePlayablePlayer.SeparatorN)
            print (f"Insert a code with {code_size} numbers (from 0 to {number_values-1}):")
            next_guess = []

            for i in range(code_size):
                next_guess.append(input(f"Number {i+1}: "))

            # Check if the input is valid
            try:
                next_guess = [int(x) for x in next_guess]
                if any(x < 0 or x >= number_values for x in next_guess):
                    raise ValueError()
                if not position.get_rules().allow_repetition() and len(set(next_guess)) != code_size:
                    print ("Code must not have repetitions. Try again:")
                    continue

            except ValueError:
                print (f"Code must be a list of integers between 0 and {number_values-1}. Try again:")
                continue

            letters = next_guess
            break

        print ("=" * WordlePlayablePlayer.SeparatorN)

        return WordleMovement(letters)


class WordleRulesGenerator(IRulesGenerator):

    @override
    def generate(
            self,
            configuration: dict) -> IGameRules:

        code_size = WordleRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['n', 'code_size'],
            required = True,
            type_cast = int,
        )

        number_values = WordleRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['m', 'number_values'],
            required = True,
            type_cast = int,
        )

        allow_repetition = WordleRulesGenerator._get_param(
            configuration=configuration,
            param_name = 'allow_repetition',
            default_value = False,
            type_cast = bool,
        )

        secret = WordleRulesGenerator._get_param(
            configuration=configuration,
            param_name = 'secret',
        )

        if secret is not None:
            if len(secret) != code_size or any(x < 0 or x >= number_values for x in secret):
                raise ValueError("Secret must be of size n and with numbers from 0 to m-1")
            if not allow_repetition and len(set(secret)) != code_size:
                raise ValueError("Secret must not have repetitions when allow_repetition is False")
        else:

            seed = WordleRulesGenerator._get_param(
                configuration=configuration,
                param_name = 'seed',
                required = True,
                type_cast = int,
            )

            rng = RandomGenerator(seed)

            secret = WordleRules.random_secret(
                code_size=code_size,
                number_values=number_values,
                rng=rng,
                allow_repetition=allow_repetition,
            )


        return WordleRules(
            code_size=code_size,
            number_values=number_values,
            secret=secret,
            allow_repetition=allow_repetition)
