"""Cards, the deck, and hand totals. No terminal I/O here."""

import random
from dataclasses import dataclass

RANKS = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")
SUITS = ("♠", "♥", "♦", "♣")
TEN_VALUE_RANKS = ("10", "J", "Q", "K")


@dataclass(frozen=True)
class Card:
    rank: str
    suit: str = "♠"

    @property
    def value(self):
        """Base value: ace counts 11 here; hand_value() lowers it when needed."""
        if self.rank == "A":
            return 11
        if self.rank in TEN_VALUE_RANKS:
            return 10
        return int(self.rank)

    def __str__(self):
        return f"{self.rank}{self.suit}"


def full_deck():
    return [Card(rank, suit) for suit in SUITS for rank in RANKS]


class Deck:
    """A single 52-card deck that refills only when empty (R3).

    `stacked` lets tests fix the order of the first cards dealt; once those run
    out the deck reshuffles a full 52 cards like normal.
    """

    def __init__(self, rng=None, stacked=None):
        self._rng = rng or random.Random()
        self.reshuffles = 0
        if stacked is not None:
            self._cards = list(stacked)
        else:
            self._cards = []
            self._refill()

    def _refill(self):
        cards = full_deck()
        self._rng.shuffle(cards)
        self._cards = cards
        self.reshuffles += 1

    def __len__(self):
        return len(self._cards)

    def draw(self):
        if not self._cards:
            self._refill()
        return self._cards.pop(0)


def hand_value(cards):
    """Best blackjack total: aces count 11 unless that would bust (R9)."""
    total = sum(card.value for card in cards)
    aces = sum(1 for card in cards if card.rank == "A")
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


def is_blackjack(cards):
    """An ace and a ten-value card as exactly two cards (R8)."""
    return len(cards) == 2 and hand_value(cards) == 21
