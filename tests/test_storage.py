import json
import random
import tempfile
import unittest
from pathlib import Path

from blackjack.cards import Card, Deck
from blackjack.game import Game
from blackjack.storage import load_high_score, save_high_score


class HighScoreStorageTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "highscore.json"

    def tearDown(self):
        self._tmp.cleanup()

    def test_r10_saved_high_score_loads_next_time(self):
        save_high_score(4500, self.path)
        self.assertEqual(load_high_score(self.path), 4500)
        self.assertEqual(Game(high_score=load_high_score(self.path)).high_score, 4500)

    def test_r10_missing_file_means_no_high_score(self):
        self.assertEqual(load_high_score(self.path), 0)

    def test_r10_corrupt_file_is_ignored(self):
        self.path.write_text("not json")
        self.assertEqual(load_high_score(self.path), 0)
        self.path.write_text('{"high_score": "lots"}')
        self.assertEqual(load_high_score(self.path), 0)

    def test_r10_current_chips_are_not_saved(self):
        deck = Deck(rng=random.Random(0), stacked=[Card(r) for r in ("10", "10", "9", "8")])
        game = Game(deck=deck)
        game.start_round(500).stand()  # chips 2500
        save_high_score(game.high_score, self.path)
        self.assertEqual(json.loads(self.path.read_text()), {"high_score": 2500})
        self.assertEqual(Game(high_score=load_high_score(self.path)).chips, 2000)


if __name__ == "__main__":
    unittest.main()
