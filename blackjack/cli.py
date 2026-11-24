"""Terminal interface. All input() and print() calls live here."""

from .cards import hand_value
from .game import BLACKJACK, BUST, DOUBLE, HIT, LOSE, MIN_BET, PUSH, SPLIT, STAND, WIN, Game
from .storage import load_high_score, save_high_score

ACTION_KEYS = {"h": HIT, "s": STAND, "d": DOUBLE, "p": SPLIT}
ACTION_LABELS = {HIT: "[h]it", STAND: "[s]tand", DOUBLE: "[d]ouble", SPLIT: "s[p]lit"}
OUTCOME_TEXT = {
    BLACKJACK: "Blackjack! Paid 3 to 2",
    WIN: "Win",
    PUSH: "Push",
    LOSE: "Lose",
    BUST: "Bust",
}


class Quit(Exception):
    pass


def ask(prompt):
    try:
        return input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        raise Quit


def show_cards(cards):
    return " ".join(str(c) for c in cards)


def show_table(rnd, reveal):
    print()
    if reveal:
        print(f"  Dealer: {show_cards(rnd.dealer)}  ({rnd.dealer_value})")
    else:
        print(f"  Dealer: {rnd.dealer[0]} ??")
    for i, hand in enumerate(rnd.hands):
        marker = ">" if not rnd.finished and i == rnd.active and len(rnd.hands) > 1 else " "
        label = f"Hand {i + 1}" if len(rnd.hands) > 1 else "You"
        line = f"{marker} {label}: {show_cards(hand.cards)}  ({hand_value(hand.cards)})  bet {hand.bet}"
        if hand.outcome:
            line += f"  -> {OUTCOME_TEXT[hand.outcome]} ({hand.net:+d})"
        print(line)


def ask_bet(game):
    while True:
        answer = ask(f"\nChips: {game.chips}  High score: {game.high_score}\n"
                     f"Bet ({MIN_BET}-{game.chips}) or q to quit: ")
        if answer == "q":
            raise Quit
        try:
            bet = int(answer)
        except ValueError:
            print("Enter a whole number.")
            continue
        error = game.bet_error(bet)
        if error:
            print(error)
            continue
        return bet


def play_round(game):
    rnd = game.start_round(ask_bet(game))
    while not rnd.finished:
        show_table(rnd, reveal=False)
        actions = rnd.available_actions()
        choice = ACTION_KEYS.get(ask(" / ".join(ACTION_LABELS[a] for a in actions) + ": "))
        if choice in actions:
            rnd.act(choice)
        else:
            print("Not an option right now.")
    show_table(rnd, reveal=True)


def main():
    game = Game(high_score=load_high_score())
    print("Blackjack practice — fake chips, no stakes.")
    print("Dealer stands on all 17s. Blackjack pays 3 to 2.")
    try:
        while True:
            if game.is_over:
                print(f"\nGame over: {game.chips} chips is below the {MIN_BET} minimum.")
                if ask("Play again with 2000 chips? [y/n]: ") != "y":
                    raise Quit
                game.new_game()
            play_round(game)
    except Quit:
        pass
    save_high_score(game.high_score)
    print(f"High score saved: {game.high_score}. Thanks for playing!")
