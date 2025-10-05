
import copy
from typing import Iterator, List, Set
from enum import Enum
import itertools
from dataclasses import dataclass

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
This game represents the Mastermind game with exact tips.
In this game there is a pattern hidden and the player must guess it.
The pattern is a list of N numbers from 0 to M-1.
The player makes guesses and the game tells how many numbers are correct and in the right position.
The game ends when the player guesses the pattern.

NOTE:
1. In this implementation, the game is played by one player, and the pattern is not known.
2. The numbers (colors) could or not be repeated depending on the configuration.
3. The game tells for each guess how many numbers are correct and in the right position, and how many are correct but in the wrong position, but not the exact position of each.
"""

class MastermindMovement(IMovement):
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
            other: "MastermindMovement"):
        return self.guess == other.guess

    def __str__(self):
        return f'{self.guess}'


class MastermindPosition(IPosition):
    """
    TODO
    """

    @dataclass
    class MastermindFeedback ():
        """Represents the feedback for a single position in the guess."""
        correct: int = 0
        misplaced: int = 0


    def __init__(
            self,
            rules: "MastermindRules",
            guesses: List[MastermindMovement],
            feedback: List[List[MastermindFeedback]]):
        super().__init__(rules)
        self._guesses = guesses
        self._feedback = feedback

    @override
    def next_player(
            self) -> PlayerIndex:
        return PlayerIndex.FirstPlayer

    def __eq__(
            self,
            other: "MastermindPosition"):
        return self._guesses == other._guesses and self._feedback == other._feedback

    def __str__(self):

        if len(self._guesses) == 0:
            return "<EMPTY POSITION>\n"

        # Print each guess in a line together with the feedback
        st = ""
        for i in range(len(self._guesses)):
            feedback_str = f'Correct: {self._feedback[i].correct}, Misplaced: {self._feedback[i].misplaced}'
            st += f'Guess {i}: {self._guesses[i]} | Feedback: {feedback_str}\n'
        return st

    def guesses(self) -> List[MastermindMovement]:
        return copy.deepcopy(self._guesses)

    def feedback(self) -> List[MastermindFeedback]:
        return copy.deepcopy(self._feedback)

    def last_guess(self) -> MastermindMovement:
        if len(self._guesses) == 0:
            return None
        return copy.deepcopy(self._guesses[-1])

    def last_feedback(self) -> MastermindFeedback:
        if len(self._feedback) == 0:
            return None
        return copy.deepcopy(self._feedback[-1])

    def code_size(self) -> int:
        return self.get_rules().code_size()

    def number_values(self) -> int:
        return self.get_rules().number_values()

    def allow_repetition(self) -> bool:
        return self.get_rules().allow_repetition()


class MastermindRules(IGameRules):

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
            possible_colors = set(range(number_values))
            colors = []
            for _ in range(code_size):
                color = rng.choice(list(possible_colors))
                colors.append(color)
                possible_colors.remove(color)
            return colors


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
            secret = MastermindRules.random_secret(
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
    def first_position(self) -> MastermindPosition:
        return MastermindPosition(self, [], [])

    @override
    def next_position(
            self,
            movement: MastermindMovement,
            position: MastermindPosition) -> MastermindPosition:
        guesses = position.guesses() + [movement]
        old_feedback = position.feedback()

        # Check if the movement is valid
        if len(movement.guess) != self.n or any(x < 0 or x >= self.m for x in movement.guess):
            raise ValueError("Movement must be of size n and with numbers from 0 to m-1")
        if not self.allow_repetition_ and len(set(movement.guess)) != self.n:
            raise ValueError("Movement must not have repetitions when allow_repetition is False")

        # Calculate the feedback of the new guess
        new_feedback = MastermindPosition.MastermindFeedback()
        secret_copy = self.__secret.copy()
        guess_copy = movement.guess.copy()
        # First pass: check for correct positions
        for i in range(self.n):
            if guess_copy[i] == secret_copy[i]:
                new_feedback.correct += 1
                secret_copy[i] = -1
                guess_copy[i] = -2
        # Second pass: check for misplaced positions
        for i in range(self.n):
            if guess_copy[i] in secret_copy:
                new_feedback.misplaced += 1
                secret_index = secret_copy.index(guess_copy[i])
                secret_copy[secret_index] = -1
                guess_copy[i] = -2

        # Append the new feedback to the list of feedbacks
        feedback = copy.deepcopy(position.feedback())
        feedback.append(new_feedback)

        return MastermindPosition(self, guesses, feedback)

    @override
    def possible_movements(
            self,
            position: MastermindPosition) -> Iterator[MastermindMovement]:

        if self.allow_repetition_:
            # Every combination of n numbers from 0 to m-1 using itertools
            for x in itertools.product(range(self.m), repeat=self.n):
                yield MastermindMovement(guess=list(x))

        else:
            # Every permutation of n numbers from 0 to m-1 using itertools
            for x in itertools.permutations(range(self.m), self.n):
                yield MastermindMovement(guess=list(x))

    @override
    def finished(
            self,
            position: MastermindPosition) -> bool:
        # Game is finished if the last guess is equal the hidden secret
        if len(position.guesses()) == 0:
            return False
        return position.guesses()[-1].guess == self.__secret

    @override
    def score(
            self,
            position: MastermindPosition) -> ScoreBoard:
        s = ScoreBoard()
        s.define_score(PlayerIndex.FirstPlayer, -len(position.guesses()))
        return s



class MastermindPlayablePlayer(IPlayer):

    SeparatorN = 40

    @override
    def play(
            self,
            position: MastermindPosition) -> IMovement:

        code_size = position.get_rules().code_size()
        number_values = position.get_rules().number_values()

        print ("=" * MastermindPlayablePlayer.SeparatorN)
        print (position)
        print ("-" * MastermindPlayablePlayer.SeparatorN)
        repetitions_text = "with repetition" if position.get_rules().allow_repetition() else "without repetition"
        print (f"Values: {list(range(position.get_rules().number_values()))}  ({repetitions_text})")

        colors = []

        while True:
            print ("-" * MastermindPlayablePlayer.SeparatorN)
            print (f"Insert a code with {code_size} numbers (from 0 to {number_values-1}):")
            next_guess = []

            for i in range(code_size):
                next_guess.append(int(input(f"Number {i+1}: ")))

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

            colors = next_guess
            break

        print ("=" * MastermindPlayablePlayer.SeparatorN)

        return MastermindMovement(colors)


class MastermindRulesGenerator(IRulesGenerator):

    @override
    def generate(
            self,
            configuration: dict) -> IGameRules:

        code_size = MastermindRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['n', 'code_size'],
            required = True,
            type_cast = int,
        )

        number_values = MastermindRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['m', 'number_values'],
            required = True,
            type_cast = int,
        )

        allow_repetition = MastermindRulesGenerator._get_param(
            configuration=configuration,
            param_name = 'allow_repetition',
            default_value = False,
            type_cast = bool,
        )

        secret = MastermindRulesGenerator._get_param(
            configuration=configuration,
            param_name = 'secret',
        )

        if secret is not None:
            if len(secret) != code_size or any(x < 0 or x >= number_values for x in secret):
                raise ValueError("Secret must be of size n and with numbers from 0 to m-1")
            if not allow_repetition and len(set(secret)) != code_size:
                raise ValueError("Secret must not have repetitions when allow_repetition is False")
        else:

            seed = MastermindRulesGenerator._get_param(
                configuration=configuration,
                param_name = 'seed',
                required = True,
                type_cast = int,
            )

            rng = RandomGenerator(seed)

            secret = MastermindRules.random_secret(
                code_size=code_size,
                number_values=number_values,
                rng=rng,
                allow_repetition=allow_repetition,
            )


        return MastermindRules(
            code_size=code_size,
            number_values=number_values,
            secret=secret,
            allow_repetition=allow_repetition)
