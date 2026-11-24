# CLAUDE.md

Guidance for working in this repository.

## Project
Terminal blackjack for no-stakes practice. Requirements are in `problem.md` (R1–R11);
`spec.md` refines them and records design decisions. Keep both in sync with the code:
if behavior changes, update `spec.md` in the same change.

## Constraints
- Python 3 **standard library only**. No third-party packages, no `requirements.txt`.
- Game logic modules (`blackjack/cards.py`, `blackjack/game.py`, `blackjack/storage.py`)
  must not call `input()` or `print()`. All terminal I/O lives in `blackjack/cli.py`.
- Randomness comes only from the `Deck`; tests inject a stacked card order.

## Commands
- Run the game: `python3 -m blackjack`
- Run all tests: `python3 -m unittest discover -s tests -v`

## Tests
- Use `unittest`. Test logic, not the page/terminal layout.
- Every test names the requirement ID(s) it checks, in the test method name
  (e.g. `test_r8_blackjack_pays_3_to_2`) and/or its docstring.
- Tests must not touch the real `highscore.json`; use a temporary directory.

## Git
- Small commits; message says what changed and why.
- Never amend or rewrite commits; fix forward with a new commit.
- `highscore.json` is runtime data and is git-ignored.
