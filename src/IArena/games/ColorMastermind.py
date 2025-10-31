
from __future__ import annotations

import copy
from typing import Iterator, List, Set
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
This game represents a version of the MasterMind game.
In this game there is a pattern hidden and the player must guess it.
The pattern is a list of N string selected between M different colors (strings).
The player makes guesses and the game tells how many strings are correct and in the right position, and how many are correct but in the wrong position.
The game ends when the player guesses the pattern.

NOTE:
1. In this implementation, the game is played by one player, and the pattern is not known.
2. The strings (colors) could or not be repeated depending on the configuration.
3. The game tells for each guess how many colors are correct and in the right position, and how many are correct but in the wrong position, but not the exact position of each.
"""

class ColorMastermindMovement(IMovement):
    """
    Represents the movement of the player in the game by guessing the pattern.
    It is a list of N strings representing the guessed colors.

    Attributes:
        guess: The guess of the player.
    """

    def __init__(
            self,
            guess: List[str]):
        self.guess = guess

    def __eq__(
            self,
            other: "ColorMastermindMovement"):
        return self.guess == other.guess

    def __str__(self):
        return f'{self.guess}'


class ColorMastermindPosition(IPosition):
    """
    Represents the position of the game at a given time.

    Methods:
        guesses(): Returns the list of guesses made so far.
        feedback(): Returns the list of feedbacks for each guess made so far.
        last_guess(): Returns the last guess made.
        last_feedback(): Returns the feedback for the last guess made.
        code_size(): Returns the size of the code.
        number_values(): Returns the number of different values (colors).
        allow_repetition(): Returns whether repetition of colors is allowed.
    """

    @dataclass
    class ColorMastermindFeedback ():
        """Represents the feedback for a single position in the guess."""
        correct: int = 0
        misplaced: int = 0


    def __init__(
            self,
            rules: "ColorMastermindRules",
            guesses: List[ColorMastermindMovement],
            feedback: List[List[ColorMastermindFeedback]]):
        super().__init__(rules)
        self._guesses : List[ColorMastermindMovement] = guesses
        self._feedback : List[ColorMastermindPosition.ColorMastermindFeedback] = feedback

    @override
    def next_player(
            self) -> PlayerIndex:
        return PlayerIndex.FirstPlayer

    def __eq__(
            self,
            other: "ColorMastermindPosition"):
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

    def guesses(self) -> List[ColorMastermindMovement]:
        return copy.deepcopy(self._guesses)

    def feedback(self) -> List[ColorMastermindFeedback]:
        return copy.deepcopy(self._feedback)

    def last_guess(self) -> ColorMastermindMovement:
        if len(self._guesses) == 0:
            return None
        return copy.deepcopy(self._guesses[-1])

    def last_feedback(self) -> ColorMastermindFeedback:
        if len(self._feedback) == 0:
            return None
        return copy.deepcopy(self._feedback[-1])

    def code_size(self) -> int:
        return self.get_rules().code_size()

    def number_values(self) -> int:
        return self.get_rules().number_values()

    def allow_repetition(self) -> bool:
        """Returns whether repetition of colors is allowed."""
        return self.get_rules().allow_repetition()

    def possible_colors(self) -> List[int]:
        """List of strings representing the possible colors in the game."""
        return self.get_rules().possible_colors()


class ColorMastermindRules(IGameRules):

    DefaultCodeSize = 5
    DefaultNumberValues = 8

    Colors_ = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'black', 'white', 'gray',
               'cyan', 'magenta', 'lime', 'teal', 'navy', 'maroon', 'olive', 'silver', 'gold', 'beige', 'coral',
               'indigo', 'ivory', 'lavender', 'salmon', 'turquoise', 'violet', 'amber', 'crimson', 'emerald', 'jade']

    @staticmethod
    def default_colors(n_colors: int) -> List[int]:
        if n_colors > len(ColorMastermindRules.Colors_):
            raise ValueError(f"n_colors must be less than or equal to {len(ColorMastermindRules.Colors_)}")
        return {c for c in ColorMastermindRules.Colors_[:n_colors]}


    @staticmethod
    def random_secret(
                code_size: int,
                possible_colors: List[str],
                rng: RandomGenerator,
                allow_repetition: bool = True) -> List[str]:

        possible_colors_set = set(possible_colors)
        number_values = len(possible_colors)
        if not allow_repetition and code_size > number_values:
            raise ValueError("n must be less than or equal to m when allow_repetition is False")
        if allow_repetition:
            indexes = [rng.randint(number_values) for _ in range(code_size)]
        else:
            colors = []
            for _ in range(code_size):
                color = rng.choice(list(possible_colors_set))
                colors.append(color)
                possible_colors_set.remove(color)
            indexes = colors

        return [possible_colors[i] for i in indexes]


    def __init__(
            self,
            code_size: int = DefaultCodeSize,
            possible_colors: List[str] = None,
            number_values: int = None,
            secret: List[str] = None,
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

        if possible_colors is None:
            if number_values is None:
                raise ValueError("Either possible_colors or number_values must be provided")
            else:
                possible_colors = ColorMastermindRules.default_colors(number_values)

        if len(set(possible_colors)) != len(possible_colors):
            raise ValueError("possible_colors must not have repetitions")

        if secret is None:
            secret = ColorMastermindRules.random_secret(
                code_size=code_size,
                number_values=number_values,
                rng=RandomGenerator(),
                allow_repetition=allow_repetition,
            )

        self.m = number_values
        self.n = code_size
        if len(secret) != code_size or any(x not in possible_colors for x in secret):
            raise ValueError("Secret must be of size n and with numbers from 0 to m-1")
        if not allow_repetition and len(set(secret)) != code_size:
            raise ValueError("Secret must not have repetitions when allow_repetition is False")
        self.__secret = secret
        self.allow_repetition_ = allow_repetition
        self.possible_colors_ = possible_colors

    def number_values(self) -> int:
        return self.m

    def code_size(self) -> int:
        return self.n

    def allow_repetition(self) -> bool:
        return self.allow_repetition_

    def possible_colors(self) -> List[int]:
        return copy.deepcopy(self.possible_colors_)

    @override
    def n_players(self) -> int:
        return 1

    @override
    def first_position(self) -> ColorMastermindPosition:
        return ColorMastermindPosition(self, [], [])

    @override
    def next_position(
            self,
            movement: ColorMastermindMovement,
            position: ColorMastermindPosition) -> ColorMastermindPosition:
        guesses = position.guesses() + [movement]
        old_feedback = position.feedback()

        # Check if the movement is valid
        if len(movement.guess) != self.n or any(x not in self.possible_colors_ for x in movement.guess):
            raise ValueError(f"Movement must be of size n and with valid colors. Incorrect movement: {movement}")
        if not self.allow_repetition_ and len(set(movement.guess)) != self.n:
            raise ValueError(f"Movement must not have repetitions when allow_repetition is False. Incorrect movement: {movement}")

        # Calculate the feedback of the new guess
        new_feedback = ColorMastermindPosition.ColorMastermindFeedback()
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

        return ColorMastermindPosition(self, guesses, feedback)

    @override
    def possible_movements(
            self,
            position: ColorMastermindPosition) -> Iterator[ColorMastermindMovement]:

        if self.allow_repetition_:
            # Every combination of n colors in possible_colors using itertools
            for x in itertools.product(self.possible_colors_, repeat=self.n):
                yield ColorMastermindMovement(guess=list(x))

        else:
            # Every permutation of n numbers from 0 to m-1 using itertools
            for x in itertools.permutations(self.possible_colors_, self.n):
                yield ColorMastermindMovement(guess=list(x))

    @override
    def finished(
            self,
            position: ColorMastermindPosition) -> bool:
        # Game is finished if the last guess is equal the hidden secret
        if len(position.guesses()) == 0:
            return False
        return position.guesses()[-1].guess == self.__secret

    @override
    def score(
            self,
            position: ColorMastermindPosition) -> ScoreBoard:
        s = ScoreBoard()
        s.define_score(PlayerIndex.FirstPlayer, -len(position.guesses()))
        return s



class ColorMastermindRulesGenerator(IRulesGenerator):

    @override
    def generate(
            self,
            configuration: dict) -> IGameRules:

        code_size = ColorMastermindRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['n', 'code_size'],
            required = True,
            type_cast = int,
        )

        number_values = ColorMastermindRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['m', 'number_values'],
            required = True,
            type_cast = int,
        )

        possible_colors = ColorMastermindRulesGenerator._get_param(
            configuration=configuration,
            param_name = 'possible_colors',
        )

        allow_repetition = ColorMastermindRulesGenerator._get_param(
            configuration=configuration,
            param_name = 'allow_repetition',
            default_value = False,
            type_cast = bool,
        )

        secret = ColorMastermindRulesGenerator._get_param(
            configuration=configuration,
            param_name = 'secret',
        )

        if secret is not None:
            if len(secret) != code_size or any(x < 0 or x >= number_values for x in secret):
                raise ValueError("Secret must be of size n and with numbers from 0 to m-1")
            if not allow_repetition and len(set(secret)) != code_size:
                raise ValueError("Secret must not have repetitions when allow_repetition is False")
        else:

            if possible_colors:
                if len(set(possible_colors)) != len(possible_colors):
                    raise ValueError("possible_colors must not have repetitions")
                elif len(possible_colors) != number_values:
                    raise ValueError("Length of possible_colors must be equal to number_values")
            else:
                possible_colors = ColorMastermindRules.default_colors(number_values)

            seed = ColorMastermindRulesGenerator._get_param(
                configuration=configuration,
                param_name = 'seed',
                required = True,
                type_cast = int,
            )

            rng = RandomGenerator(seed)

            secret = ColorMastermindRules.random_secret(
                code_size=code_size,
                possible_colors=possible_colors,
                rng=rng,
                allow_repetition=allow_repetition,
            )


        return ColorMastermindRules(
            code_size=code_size,
            possible_colors=possible_colors,
            number_values=number_values,
            secret=secret,
            allow_repetition=allow_repetition)
