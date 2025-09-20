
from copy import deepcopy
from typing import Iterator, List
import random
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
This game represents the Mastermind game with exact tips.
In this game there is a pattern hidden and the player must guess it.
The pattern is a list of N numbers from 0 to M-1.
The player makes guesses and the game tells how many numbers are correct and in the right position.
The game ends when the player guesses the pattern.

NOTE:
1. In this implementation, the game is played by one player, and the pattern is not known.
2. The numbers (colors) could be repeated.
3. The game tells for each guess exactly which numbers are correct and in the right position.
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

    class MastermindCorrectness (Enum):
        """
        Represents the correctness one number in one guess.
        """
        Wrong = 0
        Misplaced = 1
        Correct = 2

    def __init__(
            self,
            rules: "MastermindRules",
            guesses: List[MastermindMovement],
            correctness: List[List[MastermindCorrectness]]):
        super().__init__(rules)
        self.guesses = guesses
        self.correctness = correctness

    @override
    def next_player(
            self) -> PlayerIndex:
        return PlayerIndex.FirstPlayer

    def __eq__(
            self,
            other: "MastermindPosition"):
        return self.guesses == other.guesses and self.correctness == other.correctness

    def __str__(self):

        if len(self.guesses) == 0:
            return "<EMPTY POSITION>\n"

        # Print each guess in a line together with the correctness
        return "\n".join([f'{self.guesses[i]} : {[x.name for x in self.correctness[i]]}' for i in range(len(self.guesses))]) + "\n"


class MastermindRules(IGameRules):

    DefaultSizeCode = 4
    DefaultNumberColors = 6

    @staticmethod
    def random_secret(
                code_size: int,
                number_colors: int,
                rng: RandomGenerator,
                color_repetition: bool = True) -> List[int]:
        if not color_repetition and code_size > number_colors:
            raise ValueError("n must be less than or equal to m when color_repetition is False")
        if color_repetition:
            return [rng.randint(number_colors) for _ in range(code_size)]
        else:
            possible_colors = set(range(number_colors))
            colors = []
            for _ in range(code_size):
                color = rng.choice(list(possible_colors))
                colors.append(color)
                possible_colors.remove(color)
            return colors


    def __init__(
            self,
            code_size: int,
            number_colors: int,
            secret: List[int],
            allow_repetitions: bool = True):
        """
        Construct a secret code of size n with numbers from 0 to m-1.

        If a secret is not provided, a new one is generated using the seed provided.
        n and m must be provided.

        If a secret is provided, it is used instead of generating a new one.
        m must be always provided.

        Args:
            n: Size of the code.
            m: Number of colors.
            seed: Seed for the random generator.
            secret: The secret code.
        """
        self.m = number_colors
        self.n = code_size
        if len(secret) != code_size or any(x < 0 or x >= number_colors for x in secret):
            raise ValueError("Secret must be of size n and with numbers from 0 to m-1")
        if not allow_repetitions and len(set(secret)) != code_size:
            raise ValueError("Secret must not have repetitions when allow_repetitions is False")
        self.__secret = secret
        self.allow_repetitions_ = allow_repetitions

    def get_number_colors(self) -> int:
        return self.m

    def get_size_code(self) -> int:
        return self.n

    def allow_repetition(self) -> bool:
        return self.allow_repetitions_

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
        guesses = position.guesses + [movement]

        # Check if the movement is valid
        if len(movement.guess) != self.n or any(x < 0 or x >= self.m for x in movement.guess):
            raise ValueError("Movement must be of size n and with numbers from 0 to m-1")
        if not self.allow_repetitions_ and len(set(movement.guess)) != self.n:
            raise ValueError("Movement must not have repetitions when allow_repetitions is False")

        # Calculate the correctness of the new guess
        correctness = [MastermindPosition.MastermindCorrectness.Wrong for _ in range(self.n)]
        already_placed = [False for _ in range(self.n)]
        possible_misplaced = []
        for i in range(self.n):
            if movement.guess[i] == self.__secret[i]:
                correctness[i] = MastermindPosition.MastermindCorrectness.Correct
                already_placed[i] = True
            elif movement.guess[i] in self.__secret:
                possible_misplaced.append(i)

        for i in possible_misplaced:
            # Check if such number is in secret in a position that has already not being checked
            for j in range(self.n):
                if not already_placed[j] and movement.guess[i] == self.__secret[j]:
                    already_placed[j] = True
                    correctness[i] = MastermindPosition.MastermindCorrectness.Misplaced
                    break

        new_correctness = deepcopy(position.correctness)
        new_correctness.append(correctness)

        return MastermindPosition(self, guesses, new_correctness)

    @override
    def possible_movements(
            self,
            position: MastermindPosition) -> Iterator[MastermindMovement]:

        if self.allow_repetitions_:
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
        if len(position.guesses) == 0:
            return False
        return position.guesses[-1].guess == self.__secret

    @override
    def score(
            self,
            position: MastermindPosition) -> ScoreBoard:
        s = ScoreBoard()
        s.define_score(PlayerIndex.FirstPlayer, -len(position.guesses))
        return s



class MastermindPlayablePlayer(IPlayer):

    SeparatorN = 40

    @override
    def play(
            self,
            position: IPosition) -> IMovement:

        possibilities = list(position.get_rules().possible_movements(position))

        print ("=" * MastermindPlayablePlayer.SeparatorN)
        print (position)
        print ("-" * MastermindPlayablePlayer.SeparatorN)
        print ("-" * MastermindPlayablePlayer.SeparatorN)
        repetitions_text = "with repetition" if position.get_rules().allow_repetition() else "without repetition"
        print (f"Colors: {list(range(position.get_rules().get_number_colors()))}  ({repetitions_text})")

        colors = []

        for i in range(position.get_rules().get_size_code()):
            print (f"Position {i}: ", end="")
            next_color = int(input())

            if next_color < 0 or next_color >= position.get_rules().get_number_colors():
                raise ValueError(f"Color must be between 0 and {position.get_rules().get_number_colors()-1}")

            colors.append(next_color)

        print ("=" * MastermindPlayablePlayer.SeparatorN)

        return MastermindMovement(colors)


class MastermindRulesGenerator(IRulesGenerator):

    @override
    def generate(
            configuration: dict) -> IGameRules:

        code_size = MastermindRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['n', 'code_size'],
            required = True,
            type_cast = int,
        )

        number_colors = MastermindRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['m', 'number_colors'],
            required = True,
            type_cast = int,
        )

        allow_repetitions = MastermindRulesGenerator._get_param(
            configuration=configuration,
            param_name = 'allow_repetitions',
            default_value = False,
            type_cast = bool,
        )

        secret = MastermindRulesGenerator._get_param(
            configuration=configuration,
            param_name = 'secret',
        )

        if secret is not None:
            if len(secret) != code_size or any(x < 0 or x >= number_colors for x in secret):
                raise ValueError("Secret must be of size n and with numbers from 0 to m-1")
            if not allow_repetitions and len(set(secret)) != code_size:
                raise ValueError("Secret must not have repetitions when allow_repetitions is False")
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
                number_colors=number_colors,
                rng=rng,
                color_repetition=allow_repetitions,
            )


        return MastermindRules(
            code_size=code_size,
            number_colors=number_colors,
            secret=secret,
            allow_repetitions=allow_repetitions)
