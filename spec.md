# Blackjack Practice — Specification (v1)

A single-player, text-based blackjack game played in the terminal with fake chips.
It is for practice: no money, no ads, no network. Python 3 standard library only.

This document refines the requirements in `problem.md` (R1–R11). Where `problem.md`
leaves a detail open, the decision taken here is marked **Decision**.

## Program shape

- Run with `python3 -m blackjack`.
- Game logic (cards, hand values, betting, rounds, payouts, high score) lives in
  modules that do no input/output, so it can be unit tested.
- A thin command-line module handles prompts and printing.

## Requirements

### R1 — Starting chips
- A new game starts the player with **2000** chips.

### R2 — Betting
- Before each hand the player enters a whole-number bet.
- Minimum bet is **100**; maximum is all of the player's current chips.
- A bet outside that range, or not a whole number, is rejected and the player is
  asked again.
- The bet is taken from the player's chips when the hand starts.
- At the bet prompt the player may instead type `q` to quit.

### R3 — Deck
- One standard 52-card deck (4 suits × 13 ranks), shuffled at the start.
- The same deck is used across hands; cards are not returned between hands.
- When the deck is empty and a card is needed — including in the middle of a
  hand — a fresh full 52-card deck is shuffled and dealing continues.
  **Decision:** the fresh deck contains all 52 cards, including any that are
  currently on the table.

### R4 — Hit / stand
- On each of the player's hands, the player may hit (take a card) or stand.
- A hand that goes over 21 busts and its turn ends.
- **Decision:** a hand that reaches exactly 21 ends its turn automatically.

### R5 — Double down
- On a hand with exactly two cards, the player may double: the bet on that hand is
  doubled, the hand receives exactly one more card, and its turn ends.
- Allowed after a split (on each split hand's first two cards).
- **Decision:** doubling requires the player to have enough chips to match the
  hand's bet; otherwise the option is not offered.
- **Decision:** split aces cannot be doubled (they receive only one card, see R6).

### R6 — Split
- When the first two cards of the hand are a pair, the player may split them into
  two hands, each with one of the cards and a bet equal to the original bet.
  Each new hand is dealt a second card.
- **Decision:** a pair means two cards of the same rank (e.g. K-K, not K-Q).
- Only one split per round; split hands cannot be split again.
- Split aces each get exactly one more card and then stand automatically.
- **Decision:** splitting requires enough chips to cover the second bet.
- **Decision:** a split hand that totals 21 with two cards is a regular 21, not a
  blackjack, and pays 1 to 1.

### R7 — Dealer play
- The dealer draws until reaching 17 or more and stands on all 17s, including
  soft 17.
- The dealer does not draw if every player hand has busted.

### R8 — Blackjack
- A blackjack is an ace plus a ten-value card (10, J, Q, K) as the first two
  cards of an unsplit hand.
- Pays 3 to 2. **Decision:** when the bet is odd the 3:2 winnings are rounded
  down to a whole chip (e.g. bet 101 wins 151).
- **Decision:** after the initial deal, blackjacks are checked immediately. If the
  player and/or the dealer has blackjack the round ends at once: both → push,
  player only → 3:2, dealer only → player loses the bet.

### R9 — Settlement
Each player hand is compared to the dealer's hand:
- Player busts → lose the hand's bet (even if the dealer later busts).
- Dealer busts, player did not → win 1 to 1.
- Otherwise the higher total wins 1 to 1; equal totals push (bet returned).
- Hand totals: 2–10 face value, J/Q/K = 10, ace = 11 unless that would bust the
  hand, in which case it counts 1.
- Out of scope for v1: insurance, surrender, side bets.

### R10 — High score
- The high score is the largest number of chips the player has ever held. It is
  checked at the start of a game and after each hand is settled.
- When the player quits, the high score is written to `highscore.json` in the
  project directory. Current chips are **not** saved.
- On start the saved high score is loaded; if the file is missing or unreadable
  the high score starts at 0 (and immediately becomes 2000 from R1).

### R11 — Game over
- If after a hand the player has fewer than 100 chips, the game is over.
- The player is offered a new game, which resets chips to 2000 (high score kept),
  or may quit.

## Testing
- `unittest` tests cover the game logic, not the terminal layout.
- Each test names the requirement ID(s) it checks.
- Tests use a stacked (pre-ordered) deck so outcomes are deterministic.
