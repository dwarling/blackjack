"""Betting, rounds, and payouts. No terminal I/O here (see spec.md)."""

from .cards import Deck, hand_value, is_blackjack

STARTING_CHIPS = 2000
MIN_BET = 100
DEALER_STANDS_ON = 17

HIT, STAND, DOUBLE, SPLIT = "hit", "stand", "double", "split"

# Outcomes for a settled player hand.
BLACKJACK, WIN, PUSH, LOSE, BUST = "blackjack", "win", "push", "lose", "bust"


class PlayerHand:
    def __init__(self, cards, bet, from_split=False):
        self.cards = list(cards)
        self.bet = bet
        self.from_split = from_split
        self.doubled = False
        self.done = False
        self.outcome = None
        self.payout = 0  # chips returned to the player at settlement

    @property
    def value(self):
        return hand_value(self.cards)

    @property
    def busted(self):
        return self.value > 21

    @property
    def is_split_aces(self):
        return self.from_split and self.cards[0].rank == "A"

    @property
    def net(self):
        """Chips won (positive) or lost (negative) on this hand."""
        return self.payout - self.bet


class Game:
    """Holds chips, the deck, and the high score across rounds."""

    def __init__(self, deck=None, high_score=0):
        self.deck = deck or Deck()
        self.chips = STARTING_CHIPS  # R1
        self.high_score = high_score
        self._record_high_score()

    @property
    def is_over(self):
        """R11: game over when the player cannot cover the minimum bet."""
        return self.chips < MIN_BET

    def new_game(self):
        """R11: start again with fresh chips; the high score is kept."""
        self.chips = STARTING_CHIPS
        self._record_high_score()

    def bet_error(self, bet):
        """Return a message explaining why `bet` is not allowed, or None (R2)."""
        if not isinstance(bet, int) or isinstance(bet, bool):
            return "Bet must be a whole number."
        if bet < MIN_BET:
            return f"Minimum bet is {MIN_BET}."
        if bet > self.chips:
            return f"You only have {self.chips} chips."
        return None

    def start_round(self, bet):
        error = self.bet_error(bet)
        if error:
            raise ValueError(error)
        return Round(self, bet)

    def _record_high_score(self):
        """R10: the high score is the most chips ever held."""
        if self.chips > self.high_score:
            self.high_score = self.chips


class Round:
    """One hand of blackjack: deal, player decisions, dealer play, payout."""

    def __init__(self, game, bet):
        self.game = game
        self.split_done = False
        self.finished = False
        game.chips -= bet

        draw = game.deck.draw
        p1, d1, p2, d2 = draw(), draw(), draw(), draw()
        self.hands = [PlayerHand([p1, p2], bet)]
        self.dealer = [d1, d2]
        self.active = 0

        # R8: blackjacks are checked right after the deal.
        if is_blackjack(self.hands[0].cards) or is_blackjack(self.dealer):
            self._finish()

    # --- queries -------------------------------------------------------

    @property
    def current_hand(self):
        if self.finished:
            return None
        return self.hands[self.active]

    @property
    def dealer_value(self):
        return hand_value(self.dealer)

    def available_actions(self):
        hand = self.current_hand
        if hand is None:
            return []
        actions = [HIT, STAND]
        can_afford = self.game.chips >= hand.bet
        if len(hand.cards) == 2 and can_afford and not hand.is_split_aces:
            actions.append(DOUBLE)  # R5
        if (
            not self.split_done
            and len(self.hands) == 1
            and len(hand.cards) == 2
            and hand.cards[0].rank == hand.cards[1].rank
            and can_afford
        ):
            actions.append(SPLIT)  # R6
        return actions

    # --- player actions ------------------------------------------------

    def hit(self):
        hand = self._require(HIT)
        hand.cards.append(self.game.deck.draw())
        if hand.value >= 21:
            hand.done = True
        self._advance()

    def stand(self):
        hand = self._require(STAND)
        hand.done = True
        self._advance()

    def double(self):
        hand = self._require(DOUBLE)
        self.game.chips -= hand.bet
        hand.bet *= 2
        hand.doubled = True
        hand.cards.append(self.game.deck.draw())
        hand.done = True
        self._advance()

    def split(self):
        hand = self._require(SPLIT)
        self.game.chips -= hand.bet
        self.split_done = True
        first, second = hand.cards
        deck = self.game.deck
        self.hands = [
            PlayerHand([first, deck.draw()], hand.bet, from_split=True),
            PlayerHand([second, deck.draw()], hand.bet, from_split=True),
        ]
        for new_hand in self.hands:
            # R6: split aces get one card only; any 21 ends that hand's turn.
            if new_hand.is_split_aces or new_hand.value >= 21:
                new_hand.done = True
        self._advance()

    def act(self, action):
        {HIT: self.hit, STAND: self.stand, DOUBLE: self.double, SPLIT: self.split}[action]()

    # --- internals -----------------------------------------------------

    def _require(self, action):
        if action not in self.available_actions():
            raise ValueError(f"Cannot {action} now.")
        return self.current_hand

    def _advance(self):
        while self.active < len(self.hands) and self.hands[self.active].done:
            self.active += 1
        if self.active == len(self.hands):
            self._finish()

    def _finish(self):
        for hand in self.hands:
            hand.done = True
        self._play_dealer()
        self._settle()
        self.finished = True
        self.game._record_high_score()

    def _play_dealer(self):
        """R7: dealer draws to 17 and stands on all 17s, soft included."""
        if is_blackjack(self.dealer) or is_blackjack(self.hands[0].cards):
            return
        if all(hand.busted for hand in self.hands):
            return
        while self.dealer_value < DEALER_STANDS_ON:
            self.dealer.append(self.game.deck.draw())

    def _settle(self):
        """R8/R9: decide each hand and pay the player."""
        dealer_total = self.dealer_value
        dealer_bj = is_blackjack(self.dealer)
        for hand in self.hands:
            player_bj = not hand.from_split and is_blackjack(hand.cards)
            if player_bj and dealer_bj:
                outcome = PUSH
            elif player_bj:
                outcome = BLACKJACK
            elif dealer_bj:
                outcome = LOSE
            elif hand.busted:
                outcome = BUST
            elif dealer_total > 21 or hand.value > dealer_total:
                outcome = WIN
            elif hand.value == dealer_total:
                outcome = PUSH
            else:
                outcome = LOSE
            hand.outcome = outcome
            hand.payout = payout(outcome, hand.bet)
            self.game.chips += hand.payout


def payout(outcome, bet):
    """Chips returned for a hand, including the original bet."""
    if outcome == BLACKJACK:
        return bet + (bet * 3) // 2  # R8: 3 to 2, rounded down
    if outcome == WIN:
        return bet * 2
    if outcome == PUSH:
        return bet
    return 0
