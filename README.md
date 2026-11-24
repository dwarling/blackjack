# Blackjack Practice

A no-stakes blackjack game for the terminal. You play against the dealer with fake
chips to practice when to hit, stand, double down, and split — no money, no ads,
no network. Written in Python 3 using only the standard library.

- Start with 2000 chips; bets are 100 up to all your chips.
- One deck, reshuffled only after every card has been dealt.
- Hit, stand, double down (also after a split), and split pairs once per hand
  (split aces get one card each).
- Dealer stands on all 17s. Blackjack pays 3 to 2.
- Your high score (most chips ever held) is saved when you quit and shown next time.
- Drop below 100 chips and the game is over; you can start again with 2000.

Full rules and design decisions are in [spec.md](spec.md); the original requirements
are in [problem.md](problem.md).

## Run the game

```sh
python3 -m blackjack
```

At the bet prompt, enter a number or `q` to quit. During a hand, press the letter
shown for each move: `h` hit, `s` stand, `d` double, `p` split.

## Run the tests

```sh
python3 -m unittest discover -s tests -v
```

Each test name includes the requirement ID it checks (for example
`test_r8_blackjack_pays_3_to_2`).
