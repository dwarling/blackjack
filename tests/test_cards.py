import random
import unittest
from collections import Counter

from blackjack.cards import Card, Deck, full_deck, hand_value, is_blackjack


def cards(*ranks):
    return [Card(r) for r in ranks]


class DeckTests(unittest.TestCase):
    def test_r3_deck_has_52_unique_cards(self):
        deck = Deck(rng=random.Random(1))
        drawn = [deck.draw() for _ in range(52)]
        self.assertEqual(len(set(drawn)), 52)
        self.assertEqual(set(drawn), set(full_deck()))
        self.assertTrue(all(n == 4 for n in Counter(c.rank for c in drawn).values()))

    def test_r3_no_reshuffle_until_every_card_dealt(self):
        deck = Deck(rng=random.Random(2))
        for _ in range(52):
            deck.draw()
        self.assertEqual(deck.reshuffles, 1)  # only the initial shuffle
        self.assertEqual(len(deck), 0)

    def test_r3_reshuffles_when_empty_and_keeps_dealing(self):
        deck = Deck(rng=random.Random(3))
        for _ in range(52):
            deck.draw()
        card = deck.draw()
        self.assertIsInstance(card, Card)
        self.assertEqual(deck.reshuffles, 2)
        self.assertEqual(len(deck), 51)

    def test_r3_stacked_deck_deals_in_order_then_reshuffles(self):
        deck = Deck(rng=random.Random(4), stacked=cards("A", "K"))
        self.assertEqual(deck.draw().rank, "A")
        self.assertEqual(deck.draw().rank, "K")
        deck.draw()
        self.assertEqual(len(deck), 51)


class HandValueTests(unittest.TestCase):
    def test_r9_number_and_face_card_values(self):
        self.assertEqual(hand_value(cards("2", "9")), 11)
        self.assertEqual(hand_value(cards("J", "Q")), 20)
        self.assertEqual(hand_value(cards("10", "K")), 20)

    def test_r9_ace_counts_11_when_safe(self):
        self.assertEqual(hand_value(cards("A", "7")), 18)

    def test_r9_ace_counts_1_to_avoid_bust(self):
        self.assertEqual(hand_value(cards("A", "7", "9")), 17)
        self.assertEqual(hand_value(cards("A", "A")), 12)
        self.assertEqual(hand_value(cards("A", "A", "A", "A", "K")), 14)

    def test_r9_bust_over_21(self):
        self.assertEqual(hand_value(cards("K", "Q", "5")), 25)

    def test_r8_blackjack_is_ace_plus_ten_value(self):
        for ten in ("10", "J", "Q", "K"):
            self.assertTrue(is_blackjack(cards("A", ten)))
            self.assertTrue(is_blackjack(cards(ten, "A")))

    def test_r8_three_card_21_is_not_blackjack(self):
        self.assertFalse(is_blackjack(cards("7", "7", "7")))
        self.assertFalse(is_blackjack(cards("A", "9")))


if __name__ == "__main__":
    unittest.main()
