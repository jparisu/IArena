
from copy import deepcopy
from typing import Iterator, List
import random
from enum import Enum
import itertools

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex, two_player_game_change_player
from IArena.utils.decorators import override
from IArena.interfaces.Score import ScoreBoard

"""
This game represents the Mastermind game.
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
        # Print each guess in a line together with the correctness
        return "\n".join([f'{self.guesses[i]} : {[x.name for x in self.correctness[i]]}' for i in range(len(self.guesses))]) + "\n"


class MastermindRules(IGameRules):

    DefaultSizeCode = 4
    DefaultNumberColors = 6

    @staticmethod
    def get_secret(n: int, m: int, seed: int = None) -> List[int]:
        if seed is not None:
            random.seed(seed)
        return [random.randint(0, m-1) for _ in range(n)]

    def __init__(
            self,
            n: int = DefaultNumberColors,
            m: int = DefaultSizeCode,
            seed: int = None,
            secret: List[int] = None):
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
        self.m = m
        if secret:
            self.__secret = secret
            self.n = len(secret)
        else:
            self.__secret = MastermindRules.get_secret(n, m, seed)
            self.n = n

    def get_number_colors(self) -> int:
        return self.m

    def get_size_code(self) -> int:
        return self.n

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
        # Every combination of n numbers from 0 to m-1 using itertools
        return [MastermindMovement(guess = list(x))
                for x
                in itertools.product(range(self.m), repeat=self.n)]

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
        s.add_score(PlayerIndex.FirstPlayer, len(position.guesses))
        return s
