
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
The pattern is a list of N letters from 'a' to M.
The player makes guesses and the game tells how many letters are correct and in the right position.
The game ends when the player guesses the pattern.

NOTE:
1. In this implementation, the game is played by one player, and the pattern is not known.
2. The letters could or nor be repeated depending on the configuration.
3. The game tells for each guess exactly which letters are correct and in the right position.
"""

def __number_to_letter(number: int) -> str:
    return chr(ord('a') + number)

def __code_to_letters(code: List[int]) -> List[str]:
    return [__number_to_letter(x) for x in code]

class LetterWordleMovement(IMovement):
    """
    Represents the movement of the player in the game by guessing the pattern.
    It is a list of N letters with letters from 'a' to M.

    Attributes:
        guess: The guess of the player.
    """

    def __init__(
            self,
            guess: List[str]):
        self.guess = guess

    def __eq__(
            self,
            other: "LetterWordleMovement"):
        return self.guess == other.guess

    def __str__(self):
        return f'{self.guess}'


class LetterWordlePosition(IPosition):
    """
    TODO
    """

    class LetterWordleFeedback (Enum):
        """
        Represents the feedback one number in one guess.
        """
        Wrong = 0
        Misplaced = 1
        Correct = 2

    def __init__(
            self,
            rules: "LetterWordleRules",
            guesses: List[LetterWordleMovement],
            feedback: List[List[LetterWordleFeedback]]):
        super().__init__(rules)
        self._guesses = guesses
        self._feedback = feedback

    @override
    def next_player(
            self) -> PlayerIndex:
        return PlayerIndex.FirstPlayer

    def __eq__(
            self,
            other: "LetterWordlePosition"):
        return self._guesses == other._guesses and self._feedback == other._feedback

    def __str__(self):

        if len(self._guesses) == 0:
            return "<EMPTY POSITION>\n"

        # Print each guess in a line together with the feedback
        return "\n".join([f'{self._guesses[i]} : {[x.name for x in self._feedback[i]]}' for i in range(len(self._guesses))]) + "\n"

    def guesses(self) -> List[LetterWordleMovement]:
        return copy.deepcopy(self._guesses)

    def feedback(self) -> List[List[LetterWordleFeedback]]:
        return copy.deepcopy(self._feedback)

    def last_guess(self) -> LetterWordleMovement:
        if len(self._guesses) == 0:
            return None
        return copy.deepcopy(self._guesses[-1])

    def last_feedback(self) -> List[LetterWordleFeedback]:
        if len(self._feedback) == 0:
            return None
        return copy.deepcopy(self._feedback[-1])

    def code_size(self) -> int:
        return self.get_rules().code_size()

    def letters(self) -> int:
        return self.get_rules().letters()

    def allow_repetition(self) -> bool:
        return self.get_rules().allow_repetition()

    def possible_letters(self) -> List[str]:
        return self.get_rules().possible_letters()


class LetterWordleRules(IGameRules):

    DefaultCodeSize = 5
    DefaultNumberValues = 8

    @staticmethod
    def random_secret(
                code_size: int,
                letters: int,
                rng: RandomGenerator,
                allow_repetition: bool = True) -> List[str]:
        if not allow_repetition and code_size > letters:
            raise ValueError("n must be less than or equal to m when allow_repetition is False")
        if allow_repetition:
            return [rng.randint(letters) for _ in range(code_size)]
        else:
            possible_letters = set(range(letters))
            letters = []
            for _ in range(code_size):
                letter = rng.choice(list(possible_letters))
                letters.append(letter)
                possible_letters.remove(letter)
            return __code_to_letters(letters)

    @staticmethod
    def _is_correct_secret(
                code_size: int,
                letters: int,
                allow_repetition: bool,
                secret: List[str],
                throw: bool = True,
    ) -> bool:
        if letters > 26:
            if throw:
                raise ValueError("Number of letters must be less than or equal to 26")
            return False
        if len(secret) != code_size:
            if throw:
                raise ValueError(f"Secret must be of size {code_size}")
            return False
        if any(ord(x) < ord('a') or ord(x) >= ord('a') + letters for x in secret):
            if throw:
                raise ValueError(f"Secret must have letters from 'a' to '{__number_to_letter(letters - 1)}'")
            return False
        if not allow_repetition and len(set(secret)) != code_size:
            if throw:
                raise ValueError("Secret must not have repetitions when allow_repetition is False")
            return False
        return True


    def __init__(
            self,
            code_size: int = DefaultCodeSize,
            letters: int = DefaultNumberValues,
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
            letters: Number of different values (from 0 to m-1).
            secret: Seed for the random generator.
            allow_repetition: The secret code.
        """

        if secret is None:
            secret = LetterWordleRules.random_secret(
                code_size=code_size,
                letters=letters,
                rng=RandomGenerator(),
                allow_repetition=allow_repetition,
            )

        self.m = letters
        self.n = code_size

        LetterWordleRules._is_correct_secret(
                code_size=code_size,
                letters=letters,
                allow_repetition=allow_repetition,
                secret=secret,
                throw=True,
        )

        self.__secret = secret
        self.allow_repetition_ = allow_repetition

    def letters(self) -> int:
        return self.m

    def code_size(self) -> int:
        return self.n

    def allow_repetition(self) -> bool:
        return self.allow_repetition_

    def possible_letters(self) -> List[str]:
        return [__number_to_letter(i) for i in range(self.m)]

    @override
    def n_players(self) -> int:
        return 1

    @override
    def first_position(self) -> LetterWordlePosition:
        return LetterWordlePosition(self, [], [])

    @override
    def next_position(
            self,
            movement: LetterWordleMovement,
            position: LetterWordlePosition) -> LetterWordlePosition:
        guesses = position.guesses() + [movement]

        # Check if the movement is valid
        if len(movement.guess) != self.n or any(x < 0 or x >= self.m for x in movement.guess):
            raise ValueError(f"Movement must be of size {self.n} and with numbers from 0 to {self.m-1}")
        if not self.allow_repetition_ and len(set(movement.guess)) != self.n:
            raise ValueError("Movement must not have repetitions when allow_repetition is False")

        # Calculate the feedback of the new guess
        feedback = [LetterWordlePosition.LetterWordleFeedback.Wrong for _ in range(self.n)]
        already_placed = [False for _ in range(self.n)]
        possible_misplaced = []
        for i in range(self.n):
            if movement.guess[i] == self.__secret[i]:
                feedback[i] = LetterWordlePosition.LetterWordleFeedback.Correct
                already_placed[i] = True
            elif movement.guess[i] in self.__secret:
                possible_misplaced.append(i)

        for i in possible_misplaced:
            # Check if such number is in secret in a position that has already not being checked
            for j in range(self.n):
                if not already_placed[j] and movement.guess[i] == self.__secret[j]:
                    already_placed[j] = True
                    feedback[i] = LetterWordlePosition.LetterWordleFeedback.Misplaced
                    break

        new_feedback = copy.deepcopy(position.feedback())
        new_feedback.append(feedback)

        return LetterWordlePosition(self, guesses, new_feedback)

    @override
    def possible_movements(
            self,
            position: LetterWordlePosition) -> Iterator[LetterWordleMovement]:

        if self.allow_repetition_:
            # Every combination of n numbers from 0 to m-1 using itertools
            for x in itertools.product(range(self.m), repeat=self.n):
                yield LetterWordleMovement(guess=__code_to_letters(x))

        else:
            # Every permutation of n numbers from 0 to m-1 using itertools
            for x in itertools.permutations(range(self.m), self.n):
                yield LetterWordleMovement(guess=__code_to_letters(x))

    @override
    def finished(
            self,
            position: LetterWordlePosition) -> bool:
        # Game is finished if the last guess is equal the hidden secret
        if len(position.guesses()) == 0:
            return False
        return position.guesses()[-1].guess == self.__secret

    @override
    def score(
            self,
            position: LetterWordlePosition) -> ScoreBoard:
        s = ScoreBoard()
        s.define_score(PlayerIndex.FirstPlayer, -len(position.guesses()))
        return s


class LetterWordleRulesGenerator(IRulesGenerator):

    @override
    def generate(
            self,
            configuration: dict) -> IGameRules:

        code_size = LetterWordleRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['n', 'code_size'],
            required = True,
            type_cast = int,
        )

        letters = LetterWordleRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['m', 'letters'],
            required = True,
            type_cast = int,
        )

        allow_repetition = LetterWordleRulesGenerator._get_param(
            configuration=configuration,
            param_name = 'allow_repetition',
            default_value = False,
            type_cast = bool,
        )

        secret = LetterWordleRulesGenerator._get_param(
            configuration=configuration,
            param_name = 'secret',
        )

        if secret is not None:
            LetterWordleRules._is_correct_secret(
                code_size=code_size,
                letters=letters,
                allow_repetition=allow_repetition,
                secret=secret,
                throw=True,
            )
        else:

            seed = LetterWordleRulesGenerator._get_param(
                configuration=configuration,
                param_name = 'seed',
                required = True,
                type_cast = int,
            )

            rng = RandomGenerator(seed)

            secret = LetterWordleRules.random_secret(
                code_size=code_size,
                letters=letters,
                rng=rng,
                allow_repetition=allow_repetition,
            )


        return LetterWordleRules(
            code_size=code_size,
            letters=letters,
            secret=secret,
            allow_repetition=allow_repetition)
