import random
import unittest

from blackjack.cards import Card, Deck
from blackjack.game import (
    BLACKJACK, BUST, DOUBLE, HIT, LOSE, MIN_BET, PUSH, SPLIT, STAND,
    STARTING_CHIPS, WIN, Game, payout,
)


def game_with(*ranks, chips=None, high_score=0):
    """Game whose deck deals `ranks` in order: player, dealer, player, dealer, ..."""
    deck = Deck(rng=random.Random(0), stacked=[Card(r) for r in ranks])
    game = Game(deck=deck, high_score=high_score)
    if chips is not None:
        game.chips = chips
    return game


class StartingChipsTests(unittest.TestCase):
    def test_r1_player_starts_with_2000_chips(self):
        self.assertEqual(Game().chips, 2000)
        self.assertEqual(STARTING_CHIPS, 2000)


class BettingTests(unittest.TestCase):
    def test_r2_minimum_bet_is_100(self):
        game = Game()
        self.assertEqual(MIN_BET, 100)
        self.assertIsNotNone(game.bet_error(99))
        self.assertIsNone(game.bet_error(100))

    def test_r2_maximum_bet_is_all_chips(self):
        game = Game()
        self.assertIsNone(game.bet_error(2000))
        self.assertIsNotNone(game.bet_error(2001))

    def test_r2_bet_must_be_whole_number(self):
        game = Game()
        self.assertIsNotNone(game.bet_error(150.5))
        self.assertIsNotNone(game.bet_error("150"))

    def test_r2_invalid_bet_rejected_without_taking_chips(self):
        game = Game()
        with self.assertRaises(ValueError):
            game.start_round(50)
        self.assertEqual(game.chips, 2000)

    def test_r2_bet_is_taken_when_hand_starts(self):
        game = game_with("10", "9", "7", "8")
        game.start_round(300)
        self.assertEqual(game.chips, 1700)


class HitStandTests(unittest.TestCase):
    def test_r4_hit_adds_a_card(self):
        game = game_with("5", "10", "6", "8", "2")
        rnd = game.start_round(100)
        rnd.hit()
        self.assertEqual([c.rank for c in rnd.hands[0].cards], ["5", "6", "2"])
        self.assertFalse(rnd.finished)

    def test_r4_stand_ends_turn_and_dealer_plays(self):
        game = game_with("10", "10", "9", "7")  # player 19, dealer 17
        rnd = game.start_round(100)
        rnd.stand()
        self.assertTrue(rnd.finished)
        self.assertEqual(rnd.hands[0].outcome, WIN)

    def test_r4_hitting_past_21_busts_and_loses(self):
        game = game_with("10", "10", "6", "7", "K")
        rnd = game.start_round(100)
        rnd.hit()
        self.assertTrue(rnd.finished)
        self.assertEqual(rnd.hands[0].outcome, BUST)
        self.assertEqual(game.chips, 1900)

    def test_r4_hit_and_stand_always_offered_on_open_hand(self):
        rnd = game_with("10", "10", "6", "7").start_round(100)
        self.assertIn(HIT, rnd.available_actions())
        self.assertIn(STAND, rnd.available_actions())


class DoubleDownTests(unittest.TestCase):
    def test_r5_double_doubles_bet_and_takes_exactly_one_card(self):
        # player 5+6=11, dealer 10+7=17; double draws a 10 -> 21
        game = game_with("5", "10", "6", "7", "10")
        rnd = game.start_round(200)
        self.assertIn(DOUBLE, rnd.available_actions())
        rnd.double()
        hand = rnd.hands[0]
        self.assertEqual(len(hand.cards), 3)
        self.assertEqual(hand.bet, 400)
        self.assertTrue(rnd.finished)
        self.assertEqual(hand.outcome, WIN)
        self.assertEqual(game.chips, 2000 + 400)

    def test_r5_double_only_on_first_two_cards(self):
        rnd = game_with("2", "10", "3", "7", "2").start_round(100)
        rnd.hit()
        self.assertNotIn(DOUBLE, rnd.available_actions())

    def test_r5_double_not_offered_without_chips_to_cover(self):
        rnd = game_with("5", "10", "6", "7", chips=150).start_round(100)
        self.assertNotIn(DOUBLE, rnd.available_actions())

    def test_r5_double_allowed_after_split(self):
        # player 8,8 vs dealer 10,7; split hands: 8+3, 8+2
        game = game_with("8", "10", "8", "7", "3", "2", "10", "9")
        rnd = game.start_round(100)
        rnd.split()
        self.assertIn(DOUBLE, rnd.available_actions())
        rnd.double()  # first hand 8+3+10 = 21
        self.assertEqual(rnd.hands[0].bet, 200)
        self.assertIn(DOUBLE, rnd.available_actions())
        rnd.double()  # second hand 8+2+9 = 19
        self.assertTrue(rnd.finished)
        self.assertEqual([h.outcome for h in rnd.hands], [WIN, WIN])
        self.assertEqual(game.chips, 2000 + 200 + 200)


class SplitTests(unittest.TestCase):
    def test_r6_split_pair_makes_two_hands_with_equal_bets(self):
        game = game_with("8", "10", "8", "7", "3", "2")
        rnd = game.start_round(100)
        self.assertIn(SPLIT, rnd.available_actions())
        rnd.split()
        self.assertEqual(len(rnd.hands), 2)
        self.assertEqual([h.bet for h in rnd.hands], [100, 100])
        self.assertEqual([[c.rank for c in h.cards] for h in rnd.hands], [["8", "3"], ["8", "2"]])
        self.assertEqual(game.chips, 1800)

    def test_r6_no_split_on_non_pair(self):
        rnd = game_with("K", "10", "Q", "7").start_round(100)
        self.assertNotIn(SPLIT, rnd.available_actions())

    def test_r6_split_only_once_per_hand(self):
        game = game_with("8", "10", "8", "7", "8", "8")
        rnd = game.start_round(100)
        rnd.split()
        self.assertEqual([c.rank for c in rnd.current_hand.cards], ["8", "8"])
        self.assertNotIn(SPLIT, rnd.available_actions())

    def test_r6_split_aces_get_one_card_each(self):
        game = game_with("A", "10", "A", "7", "5", "9")
        rnd = game.start_round(100)
        rnd.split()
        self.assertTrue(rnd.finished)
        self.assertEqual([len(h.cards) for h in rnd.hands], [2, 2])

    def test_r6_split_hand_21_is_not_blackjack(self):
        # split aces each get a ten: 21 pays 1:1, not 3:2
        game = game_with("A", "10", "A", "7", "K", "Q")
        rnd = game.start_round(100)
        rnd.split()
        self.assertEqual([h.outcome for h in rnd.hands], [WIN, WIN])
        self.assertEqual(game.chips, 2000 + 100 + 100)

    def test_r6_split_not_offered_without_chips_to_cover(self):
        rnd = game_with("8", "10", "8", "7", chips=150).start_round(100)
        self.assertNotIn(SPLIT, rnd.available_actions())


class DealerTests(unittest.TestCase):
    def test_r7_dealer_hits_below_17(self):
        game = game_with("10", "10", "8", "6", "5")  # dealer 16 -> draws 5 = 21
        rnd = game.start_round(100)
        rnd.stand()
        self.assertEqual(rnd.dealer_value, 21)
        self.assertEqual(rnd.hands[0].outcome, LOSE)

    def test_r7_dealer_stands_on_soft_17(self):
        game = game_with("10", "A", "8", "6", "5")  # dealer A+6 = soft 17
        rnd = game.start_round(100)
        rnd.stand()
        self.assertEqual(len(rnd.dealer), 2)
        self.assertEqual(rnd.dealer_value, 17)
        self.assertEqual(rnd.hands[0].outcome, WIN)

    def test_r7_dealer_stands_on_hard_17(self):
        game = game_with("10", "10", "8", "7", "5")
        rnd = game.start_round(100)
        rnd.stand()
        self.assertEqual(len(rnd.dealer), 2)

    def test_r7_dealer_does_not_draw_when_player_busted(self):
        game = game_with("10", "10", "6", "2", "K", "5")
        rnd = game.start_round(100)
        rnd.hit()
        self.assertEqual(len(rnd.dealer), 2)


class BlackjackTests(unittest.TestCase):
    def test_r8_blackjack_pays_3_to_2(self):
        game = game_with("A", "10", "K", "7")
        rnd = game.start_round(200)
        self.assertTrue(rnd.finished)
        self.assertEqual(rnd.hands[0].outcome, BLACKJACK)
        self.assertEqual(game.chips, 2000 + 300)

    def test_r8_odd_bet_blackjack_rounds_down(self):
        self.assertEqual(payout(BLACKJACK, 101), 101 + 151)

    def test_r8_both_blackjack_push(self):
        game = game_with("A", "A", "K", "Q")
        rnd = game.start_round(100)
        self.assertEqual(rnd.hands[0].outcome, PUSH)
        self.assertEqual(game.chips, 2000)

    def test_r8_dealer_blackjack_beats_player_immediately(self):
        game = game_with("10", "A", "9", "K")
        rnd = game.start_round(100)
        self.assertTrue(rnd.finished)
        self.assertEqual(rnd.hands[0].outcome, LOSE)
        self.assertEqual(game.chips, 1900)


class SettlementTests(unittest.TestCase):
    def test_r9_higher_total_wins_1_to_1(self):
        game = game_with("10", "10", "9", "8")
        game.start_round(100).stand()
        self.assertEqual(game.chips, 2100)

    def test_r9_lower_total_loses(self):
        game = game_with("10", "10", "7", "8")
        game.start_round(100).stand()
        self.assertEqual(game.chips, 1900)

    def test_r9_equal_totals_push(self):
        game = game_with("10", "10", "8", "8")
        rnd = game.start_round(100)
        rnd.stand()
        self.assertEqual(rnd.hands[0].outcome, PUSH)
        self.assertEqual(game.chips, 2000)

    def test_r9_dealer_bust_player_wins(self):
        game = game_with("10", "10", "2", "6", "K")  # dealer 16 + K = 26
        rnd = game.start_round(100)
        rnd.stand()
        self.assertEqual(rnd.hands[0].outcome, WIN)
        self.assertEqual(game.chips, 2100)

    def test_r9_payout_amounts(self):
        self.assertEqual(payout(WIN, 100), 200)
        self.assertEqual(payout(PUSH, 100), 100)
        self.assertEqual(payout(LOSE, 100), 0)
        self.assertEqual(payout(BUST, 100), 0)

    def test_r3_deck_reshuffles_mid_hand_and_hand_continues(self):
        game = game_with("10", "10", "6", "7")  # only 4 stacked cards
        rnd = game.start_round(100)
        self.assertEqual(len(game.deck), 0)
        rnd.hit()  # deck must reshuffle to deal this card
        self.assertEqual(len(rnd.hands[0].cards), 3)
        self.assertEqual(game.deck.reshuffles, 1)


class HighScoreTests(unittest.TestCase):
    def test_r10_high_score_starts_at_least_starting_chips(self):
        self.assertEqual(Game(high_score=0).high_score, 2000)
        self.assertEqual(Game(high_score=5000).high_score, 5000)

    def test_r10_high_score_tracks_most_chips_held(self):
        game = game_with("10", "10", "9", "8", "10", "10", "7", "8")
        game.start_round(1000).stand()  # win -> 3000
        self.assertEqual(game.high_score, 3000)
        game.start_round(1000).stand()  # lose -> 2000
        self.assertEqual(game.chips, 2000)
        self.assertEqual(game.high_score, 3000)


class GameOverTests(unittest.TestCase):
    def test_r11_game_over_below_minimum_bet(self):
        game = game_with("10", "10", "7", "8")
        game.start_round(1950).stand()
        self.assertEqual(game.chips, 50)
        self.assertTrue(game.is_over)

    def test_r11_not_over_at_exactly_minimum(self):
        game = Game()
        game.chips = 100
        self.assertFalse(game.is_over)

    def test_r11_new_game_resets_chips_keeps_high_score(self):
        game = Game(high_score=9000)
        game.chips = 0
        game.new_game()
        self.assertEqual(game.chips, 2000)
        self.assertEqual(game.high_score, 9000)


if __name__ == "__main__":
    unittest.main()
