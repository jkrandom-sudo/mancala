"""Tests for game.py — menu and round loop."""
import io
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import game
import settings as settings_mod
import score as score_mod
from sound import Sound


class StackedInput:
    def __init__(self, lines):
        self.lines = list(lines)
        self.prompts = []

    def __call__(self, prompt=""):
        self.prompts.append(prompt)
        if not self.lines:
            raise EOFError()
        return self.lines.pop(0)


class ParsePitTest(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(game.parse_pit("1"), 0)
        self.assertEqual(game.parse_pit("6"), 5)
        self.assertEqual(game.parse_pit("  3  "), 2)

    def test_invalid(self):
        self.assertIsNone(game.parse_pit("0"))
        self.assertIsNone(game.parse_pit("7"))
        self.assertIsNone(game.parse_pit(""))
        self.assertIsNone(game.parse_pit("a"))
        self.assertIsNone(game.parse_pit("1.5"))


class PlayRoundTest(unittest.TestCase):
    def _settings(self, lang="en", difficulty="easy"):
        return {"lang": lang, "sound": False, "volume": 0, "difficulty": difficulty}

    def test_quit(self):
        out = io.StringIO()
        s = self._settings()
        sound = Sound(enabled=False, output=out)
        result = game.play_round(s, sound, StackedInput(["q"]), out, rng=random.Random(0))
        self.assertIsNone(result)

    def test_invalid_pit_message(self):
        out = io.StringIO()
        s = self._settings()
        sound = Sound(enabled=False, output=out)
        # Bad input then quit
        game.play_round(s, sound, StackedInput(["abc", "q"]), out, rng=random.Random(0))
        self.assertIn("Bad pit", out.getvalue())

    def test_eof_raises_quitgame(self):
        out = io.StringIO()
        s = self._settings()
        sound = Sound(enabled=False, output=out)
        with self.assertRaises(game.QuitGame):
            game.play_round(s, sound, StackedInput([]), out, rng=random.Random(0))

    def test_full_game_terminates(self):
        out = io.StringIO()
        s = self._settings(difficulty="easy")
        sound = Sound(enabled=False, output=out)
        # Feed pit 3 (extra turn opening) then ad-nauseum 1's; loop will fall through invalids
        # Use a long pool of pit choices; play_round terminates when game over.
        moves = []
        for _ in range(200):
            moves.extend(["1", "2", "3", "4", "5", "6"])
        result = game.play_round(s, sound, StackedInput(moves), out, rng=random.Random(0))
        # Game must have finished (result not None)
        self.assertIsNotNone(result)
        self.assertIn(result["result"], ("win", "loss", "tie"))

    def test_undo_command(self):
        out = io.StringIO()
        s = self._settings()
        sound = Sound(enabled=False, output=out)
        # Move pit 1 (no extra turn → AI plays), then undo → back to player turn, then quit
        game.play_round(s, sound, StackedInput(["1", "u", "q"]), out, rng=random.Random(0))
        # Should have undone (no error)
        self.assertNotIn("Nothing to undo", out.getvalue())

    def test_undo_empty_message(self):
        out = io.StringIO()
        s = self._settings()
        sound = Sound(enabled=False, output=out)
        game.play_round(s, sound, StackedInput(["u", "q"]), out, rng=random.Random(0))
        self.assertIn("Nothing to undo", out.getvalue())

    def test_reset_command(self):
        out = io.StringIO()
        s = self._settings()
        sound = Sound(enabled=False, output=out)
        game.play_round(s, sound, StackedInput(["1", "r", "q"]), out, rng=random.Random(0))
        self.assertIn("reset", out.getvalue().lower())

    def test_hint_command(self):
        out = io.StringIO()
        s = self._settings()
        sound = Sound(enabled=False, output=out)
        game.play_round(s, sound, StackedInput(["h", "q"]), out, rng=random.Random(0))
        self.assertIn("Hint", out.getvalue())


class MainMenuTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = Path(self._tmp.name)
        self._patches = [
            patch.object(settings_mod, "DEFAULT_PATH", tmp / "s.json"),
            patch.object(score_mod, "DEFAULT_PATH", tmp / "scores.json"),
        ]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in self._patches:
            p.stop()
        self._tmp.cleanup()

    def test_quit(self):
        out = io.StringIO()
        game.main_menu(StackedInput(["q"]), out, rng=random.Random(0))
        text = out.getvalue()
        self.assertTrue("Bye" in text or "再见" in text)

    def test_unknown_choice(self):
        out = io.StringIO()
        game.main_menu(StackedInput(["x", "q"]), out, rng=random.Random(0))
        text = out.getvalue()
        self.assertTrue("Unknown" in text or "未知" in text)

    def test_help_flow(self):
        out = io.StringIO()
        game.main_menu(StackedInput(["h", "", "q"]), out, rng=random.Random(0))
        text = out.getvalue()
        self.assertTrue("help" in text.lower() or "帮助" in text)

    def test_scores_empty(self):
        out = io.StringIO()
        game.main_menu(StackedInput(["l", "", "q"]), out, rng=random.Random(0))
        text = out.getvalue()
        self.assertTrue("No scores" in text or "暂无" in text)

    def test_settings_back(self):
        out = io.StringIO()
        game.main_menu(StackedInput(["s", "b", "q"]), out, rng=random.Random(0))
        self.assertTrue(settings_mod.DEFAULT_PATH.exists())

    def test_settings_cycle_lang(self):
        out = io.StringIO()
        game.main_menu(StackedInput(["s", "1", "b", "q"]), out, rng=random.Random(0))
        s = settings_mod.load()
        self.assertEqual(s["lang"], "en")

    def test_settings_toggle_sound(self):
        out = io.StringIO()
        game.main_menu(StackedInput(["s", "2", "b", "q"]), out, rng=random.Random(0))
        s = settings_mod.load()
        self.assertFalse(s["sound"])

    def test_settings_cycle_volume(self):
        out = io.StringIO()
        game.main_menu(StackedInput(["s", "3", "b", "q"]), out, rng=random.Random(0))
        s = settings_mod.load()
        self.assertEqual(s["volume"], 2)

    def test_settings_cycle_difficulty(self):
        out = io.StringIO()
        game.main_menu(StackedInput(["s", "4", "b", "q"]), out, rng=random.Random(0))
        s = settings_mod.load()
        self.assertEqual(s["difficulty"], "hard")

    def test_eof_exits_main_menu(self):
        out = io.StringIO()
        game.main_menu(StackedInput([]), out, rng=random.Random(0))
        text = out.getvalue()
        self.assertTrue("Bye" in text or "再见" in text)

    def test_play_then_save_score(self):
        settings_mod.save({"lang": "en", "sound": False, "volume": 0, "difficulty": "easy"})
        out = io.StringIO()
        fake_result = {"won": True, "result": "win", "score": 150, "diff": 5, "difficulty": "easy"}
        with patch.object(game, "play_round", return_value=fake_result):
            game.main_menu(StackedInput(["p", "Bob", "q"]), out, rng=random.Random(0))
        scores = score_mod.load()
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]["name"], "Bob")
        self.assertEqual(scores[0]["score"], 150)

    def test_play_skip_save(self):
        settings_mod.save({"lang": "en", "sound": False, "volume": 0, "difficulty": "easy"})
        out = io.StringIO()
        fake_result = {"won": True, "result": "win", "score": 150, "diff": 5, "difficulty": "easy"}
        with patch.object(game, "play_round", return_value=fake_result):
            game.main_menu(StackedInput(["p", "", "q"]), out, rng=random.Random(0))
        scores = score_mod.load()
        self.assertEqual(scores, [])

    def test_play_quit_round_does_not_save(self):
        settings_mod.save({"lang": "en", "sound": False, "volume": 0, "difficulty": "easy"})
        out = io.StringIO()
        # play_round returns None on quit — no save prompt
        with patch.object(game, "play_round", return_value=None):
            game.main_menu(StackedInput(["p", "q"]), out, rng=random.Random(0))
        scores = score_mod.load()
        self.assertEqual(scores, [])


if __name__ == "__main__":
    unittest.main()
