
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
This game represents the NumberGuess game.
In this game there is a number hidden and the player must guess it.
The number is between 0 to M-1.
The player makes guesses.
The game ends when the player guesses the number.

NOTE:
1. In this implementation, the game is played by one player, and the pattern is not known.
"""

class NumberGuessMovement(IMovement):
    """
    Represents the movement of the player in the game by guessing the pattern.
    It is a number between 0 to M-1.

    Attributes:
        guess: The guess of the player.
    """

    def __init__(
            self,
            guess: int):
        self.guess = guess

    def __eq__(
            self,
            other: "NumberGuessMovement"):
        return self.guess == other.guess

    def __str__(self):
        return f'{{{self.guess}}}'


class NumberGuessPosition(IPosition):
    """
    TODO
    """

    def __init__(
            self,
            rules: "NumberGuessRules",
            guesses: List[NumberGuessMovement]):
        super().__init__(rules)
        self._guesses = guesses

    @override
    def next_player(
            self) -> PlayerIndex:
        return PlayerIndex.FirstPlayer

    def __eq__(
            self,
            other: "NumberGuessPosition"):
        return self._guesses == other._guesses

    def __str__(self):

        if len(self._guesses) == 0:
            return "<EMPTY POSITION>\n"

        # Print each guess in a line together with the feedback
        return "{" + ", ".join([f'{self._guesses[i]}' for i in range(len(self._guesses))]) + "}"

    def guesses(self) -> List[NumberGuessMovement]:
        return copy.deepcopy(self._guesses)

    def last_guess(self) -> NumberGuessMovement:
        if len(self._guesses) == 0:
            return None
        return copy.deepcopy(self._guesses[-1])

    def number_values(self) -> int:
        return self.get_rules().number_values()


class NumberGuessRules(IGameRules):

    DefaultNumberValues = 8

    @staticmethod
    def random_secret(
                number_values: int,
                rng: RandomGenerator) -> int:
        return rng.randint(number_values)

    def __init__(
            self,
            number_values: int = DefaultNumberValues,
            secret: int = None):
        """
        TODO
        """

        if secret is None:
            secret = NumberGuessRules.random_secret(
                number_values=number_values,
                rng=RandomGenerator(),
            )

        self.m = number_values
        self.__secret = secret

        if self.__secret < 0 or self.__secret >= self.m:
            raise ValueError("Secret must be between 0 and m-1")

    def number_values(self) -> int:
        return self.m

    @override
    def n_players(self) -> int:
        return 1

    @override
    def first_position(self) -> NumberGuessPosition:
        return NumberGuessPosition(self, [])

    @override
    def next_position(
            self,
            movement: NumberGuessMovement,
            position: NumberGuessPosition) -> NumberGuessPosition:

        # Check if the movement is valid
        if movement.guess < 0 or movement.guess >= self.m:
            raise ValueError(f"Movement must be between 0 and {self.m-1}")

        # Create new list of guesses
        guesses = position.guesses() + [movement]

        return NumberGuessPosition(self, guesses)

    @override
    def possible_movements(
            self,
            position: NumberGuessPosition) -> Iterator[NumberGuessMovement]:

        # Values from 0 to m-1
        for i in range(self.m):
            yield NumberGuessMovement(i)

    @override
    def finished(
            self,
            position: NumberGuessPosition) -> bool:
        # Game is finished if the last guess is equal the hidden secret
        if position.last_guess() is not None and position.last_guess().guess == self.__secret:
            return True
        return False

    @override
    def score(
            self,
            position: NumberGuessPosition) -> ScoreBoard:
        s = ScoreBoard()
        s.define_score(PlayerIndex.FirstPlayer, -len(position.guesses()))
        return s



class NumberGuessPlayablePlayer(IPlayer):

    SeparatorN = 40

    @override
    def play(
            self,
            position: NumberGuessPosition) -> IMovement:

        number_values = position.get_rules().number_values()

        print ("=" * NumberGuessPlayablePlayer.SeparatorN)
        print (f"Previous guesses: {position}")
        print ("-" * NumberGuessPlayablePlayer.SeparatorN)
        print (f"Values: {list(range(number_values))})")

        guess = None

        while True:
            print ("-" * NumberGuessPlayablePlayer.SeparatorN)
            print (f"Insert a number (from 0 to {number_values-1}):")
            guess = None

            # Check if the input is valid
            try:
                guess = int(input())
                if guess < 0 or guess >= number_values:
                    raise ValueError()

            except ValueError:
                print (f"Code must be an integer between 0 and {number_values-1}. Try again:")
                continue

            break

        print ("=" * NumberGuessPlayablePlayer.SeparatorN)

        return NumberGuessMovement(guess)



class NumberGuessRulesGenerator(IRulesGenerator):

    @override
    def generate(
            self,
            configuration: dict) -> IGameRules:

        number_values = NumberGuessRulesGenerator._get_param(
            configuration=configuration,
            param_names = ['m', 'number_values'],
            required = True,
            type_cast = int,
        )

        secret = NumberGuessRulesGenerator._get_param(
            configuration=configuration,
            param_name = 'secret',
        )

        if secret is not None:
            if secret < 0 or secret >= number_values:
                raise ValueError("Secret must be between 0 and m-1")
        else:

            seed = NumberGuessRulesGenerator._get_param(
                configuration=configuration,
                param_name = 'seed',
                required = True,
                type_cast = int,
            )

            rng = RandomGenerator(seed)

            secret = NumberGuessRules.random_secret(
                number_values=number_values,
                rng=rng,
            )


        return NumberGuessRules(
            number_values=number_values,
            secret=secret)
