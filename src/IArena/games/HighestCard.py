
from typing import Dict, Iterator, List
import random
from copy import deepcopy

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.utils.decorators import override
from IArena.interfaces.Score import ScoreBoard

"""
This game represents the HighestCard game.
In this game N players has M cards from 0 to N*M-1.
The players must bet how many rounds it will win.
Then in each round all players play its highest card, and wins the highest of the cards played.

Players that has accurately bet the number of rounds won gets -5 points.
Players that bet less than the number of rounds won gets 1 point for each round less.
Players that bet more than the number of rounds won gets 2 point for each round more.
"""

class HighestCardMovement(IMovement):
    """
    Represents the bet of the player.
    It is a number between 0 and M.

    Attributes:
        bet: int: The guess of how many rounds the player will win.
    """

    def __init__(
            self,
            bet: int):
        self.bet = bet

    def __eq__(
            self,
            other: "HighestCardMovement"):
        return self.bet == other.bet

    def __str__(self):
        return f'<{self.bet}>'


class HighestCardPosition(IPosition):
    """
    Represents a position where some players has already bet.
    The bets are taken secretly.
    """

    def __init__(
            self,
            cards: Dict[PlayerIndex, List[int]] = None,
            next_bet: HighestCardMovement = None,
            previous: "HighestCardPosition" = None):
        if cards is not None:
            self.__cards = cards
            self.__bet = {}

        else:
            self.__cards = deepcopy(previous.__cards)
            self.__bet = deepcopy(previous.__bet)
            self.__bet[self.next_player()] = next_bet

    @override
    def next_player(
            self) -> PlayerIndex:
        # The next player is the one that has not bet yet
        if self.__bet == {}:
            return PlayerIndex.FirstPlayer
        return max(self.__bet.keys()) + 1

    def get_cards(self) -> List[int]:
        return deepcopy(self.__cards[self.next_player()])

    def number_players(self) -> int:
        return len(self.__cards)

    def number_cards(self) -> int:
        return len(self.__cards[0])

    def __eq__(
            self,
            other: "HighestCardPosition"):
        return self.__bet == other.__bet

    def __str__(self):
        # Print each guess in a line together with the correctness
        return f'{{ Next player: {self.next_player()} | Cards: {self.__cards[self.next_player()]}}}'

    def _calculate_score(self) -> ScoreBoard:
        # Calculate how many rounds each player has won
        round_win = [0 for _ in range(self.number_players())]
        for i in range(self.number_cards()):
            max_player = -1
            max_card = -1
            for j in range(self.number_players()):
                if self.__cards[j][i] > max_card:
                    max_card = self.__cards[j][i]
                    max_player = j
            round_win[max_player] += 1

        # Calculate the score of each player depending on its bet
        score = {}
        score = ScoreBoard()
        for i in range(self.number_players()):
            if self.__bet[i].bet == round_win[i]:
                score.add_score(i, -5)
            elif self.__bet[i].bet < round_win[i]:
                score.add_score(i, 1 * (round_win[i] - self.__bet[i].bet))
            else:
                score.add_score(i, 2 * (self.__bet[i].bet - round_win[i]))

        return score


class HighestCardRules(IGameRules):

    def __init__(
            self,
            cards_distribution: Dict[PlayerIndex, List[int]] = None,
            n_players: int = 3,
            m_cards: int = 4,
            seed: int = None):

        if cards_distribution is None:
            cards = [i for i in range(n_players*m_cards)]

            if seed is not None:
                random.seed(seed)

            random.shuffle(cards)

            self.__cards = {}

            for i in range(n_players):
                self.__cards[i] = []
                for _ in range(m_cards):
                    self.__cards[i].append(cards.pop())

        else:
            self.__cards = cards_distribution

        # Sort the cards of each player
        for i in range(n_players):
            self.__cards[i].sort()

        self.n = len(self.__cards)
        self.m = len(self.__cards[0])


    @override
    def n_players(self) -> int:
        return self.n

    def m_cards(self) -> int:
        return self.m

    @override
    def first_position(self) -> HighestCardPosition:
        return HighestCardPosition(
            cards=self.__cards
        )

    @override
    def next_position(
            self,
            movement: HighestCardMovement,
            position: HighestCardPosition) -> HighestCardPosition:
        return HighestCardPosition(
            next_bet=movement,
            previous=position
        )

    @override
    def possible_movements(
            self,
            position: HighestCardPosition) -> Iterator[HighestCardMovement]:
        # The possible movements are the numbers between 0 and M
        return [HighestCardMovement(i) for i in range(self.m + 1)]

    @override
    def finished(
            self,
            position: HighestCardPosition) -> bool:
        # Finished when all players has bet
        return position.next_player() == self.n

    @override
    def score(
            self,
            position: HighestCardPosition) -> ScoreBoard:
        return position._calculate_score()
