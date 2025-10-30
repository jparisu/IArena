
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
The player makes guesses and the game tells how far each number is from the correct position.
The game ends when the player guesses the pattern.

NOTE:
1. In this implementation, the game is played by one player, and the pattern is not known.
2. The numbers (letters in actual game) could or nor be repeated depending on the configuration.
3. The game tells for each guess how far each number is from the correct position (in absolute value), or -1 if the number is not in the pattern.
"""

class DistanceWordleMovement(IMovement):
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
            other: "DistanceWordleMovement"):
        return self.guess == other.guess

    def __str__(self):
        return f'{self.guess}'


class DistanceWordlePosition(IPosition):
    """
    Represents the position of the game at a given moment.

    Methods:
        guesses: Returns the list of guesses made so far.
        feedback: Returns the list of feedbacks received so far.
        last_guess: Returns the last guess made.
        last_feedback: Returns the last feedback received.
        code_size: Returns the size of the code.
        number_values: Returns the number of different values.
        allow_repetition: Returns whether repetition is allowed in the code.
    """

    def __init__(
            self,
            rules: "DistanceWordleRules",
            guesses: List[DistanceWordleMovement],
            feedback: List[List[int]]):
        super().__init__(rules)
        self._guesses = guesses
        self._feedback = feedback

    @override
    def next_player(
            self) -> PlayerIndex:
        return PlayerIndex.FirstPlayer

    def __eq__(
            self,
            other: "DistanceWordlePosition"):
        return self._guesses == other._guesses and self._feedback == other._feedback

    def __str__(self):

        if len(self._guesses) == 0:
            return "<EMPTY POSITION>\n"

        # Print each guess in a line together with the feedback
        return "\n".join([f'{self._guesses[i]} : {[x.name for x in self._feedback[i]]}' for i in range(len(self._guesses))]) + "\n"

    def guesses(self) -> List[DistanceWordleMovement]:
        return copy.deepcopy(self._guesses)

    def feedback(self) -> List[List[int]]:
        return copy.deepcopy(self._feedback)

    def last_guess(self) -> DistanceWordleMovement:
        if len(self._guesses) == 0:
            return None
        return copy.deepcopy(self._guesses[-1])

    def last_feedback(self) -> List[int]:
        if len(self._feedback) == 0:
            return None
        return copy.deepcopy(self._feedback[-1])

    def code_size(self) -> int:
        return self.get_rules().code_size()

    def number_values(self) -> int:
        return self.get_rules().number_values()

    def allow_repetition(self) -> bool:
        return self.get_rules().allow_repetition()


class DistanceWordleRules(IGameRules):

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
            secret = DistanceWordleRules.random_secret(
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
    def first_position(self) -> DistanceWordlePosition:
        return DistanceWordlePosition(self, [], [])

    @override
    def next_position(
            self,
            movement: DistanceWordleMovement,
            position: DistanceWordlePosition) -> DistanceWordlePosition:
        guesses = position.guesses() + [movement]

        # Check if the movement is valid
        if len(movement.guess) != self.n or any(x < 0 or x >= self.m for x in movement.guess):
            raise ValueError(f"Movement must be of size {self.n} and with numbers from 0 to {self.m-1}")
        if not self.allow_repetition_ and len(set(movement.guess)) != self.n:
            raise ValueError("Movement must not have repetitions when allow_repetition is False")

        # Calculate the feedback of the new guess
        feedback = [self.code_size() for _ in range(self.n)]
        already_placed = [False for _ in range(self.n)]
        possible_misplaced = []
        for i in range(self.n):
            if movement.guess[i] == self.__secret[i]:
                feedback[i] = 0
                already_placed[i] = True
            elif movement.guess[i] in self.__secret:
                possible_misplaced.append(i)

        for i in possible_misplaced:
            # Check if such number is in secret in a position that has already not being checked
            for j in range(self.n):
                if not already_placed[j] and movement.guess[i] == self.__secret[j]:
                    already_placed[j] = True
                    feedback[i] = abs(i - j)
                    break

        new_feedback = copy.deepcopy(position.feedback())
        new_feedback.append(feedback)

        return DistanceWordlePosition(self, guesses, new_feedback)

    @override
    def possible_movements(
            self,
            position: DistanceWordlePosition) -> Iterator[DistanceWordleMovement]:

        if self.allow_repetition_:
            # Every combination of n numbers from 0 to m-1 using itertools
            for x in itertools.product(range(self.m), repeat=self.n):
                yield DistanceWordleMovement(guess=list(x))

        else:
            # Every permutation of n numbers from 0 to m-1 using itertools
            for x in itertools.permutations(range(self.m), self.n):
                yield DistanceWordleMovement(guess=list(x))

    @override
    def finished(
            self,
            position: DistanceWordlePosition) -> bool:
        # Game is finished if the last guess is equal the hidden secret
        if len(position.guesses()) == 0:
            return False
        return position.guesses()[-1].guess == self.__secret

    @override
    def score(
            self,
            position: DistanceWordlePosition) -> ScoreBoard:
        s = ScoreBoard()
        s.define_score(PlayerIndex.FirstPlayer, -len(position.guesses()))
        return s



class DistanceWordleRulesGenerator(IRulesGenerator):

    @override
    def generate(
            self,
            configuration: dict) -> IGameRules:

        code_size = DistanceWordleRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['n', 'code_size'],
            required = True,
            type_cast = int,
        )

        number_values = DistanceWordleRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['m', 'number_values'],
            required = True,
            type_cast = int,
        )

        allow_repetition = DistanceWordleRulesGenerator._get_param(
            configuration=configuration,
            param_name = 'allow_repetition',
            default_value = False,
            type_cast = bool,
        )

        secret = DistanceWordleRulesGenerator._get_param(
            configuration=configuration,
            param_name = 'secret',
        )

        if secret is not None:
            if len(secret) != code_size or any(x < 0 or x >= number_values for x in secret):
                raise ValueError("Secret must be of size n and with numbers from 0 to m-1")
            if not allow_repetition and len(set(secret)) != code_size:
                raise ValueError("Secret must not have repetitions when allow_repetition is False")
        else:

            seed = DistanceWordleRulesGenerator._get_param(
                configuration=configuration,
                param_name = 'seed',
                required = True,
                type_cast = int,
            )

            rng = RandomGenerator(seed)

            secret = DistanceWordleRules.random_secret(
                code_size=code_size,
                number_values=number_values,
                rng=rng,
                allow_repetition=allow_repetition,
            )


        return DistanceWordleRules(
            code_size=code_size,
            number_values=number_values,
            secret=secret,
            allow_repetition=allow_repetition)
