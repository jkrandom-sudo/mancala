"""Tests for settings, score, sound, i18n."""
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import settings as settings_mod
import score as score_mod
from sound import Sound
from i18n import t, STRINGS


class SettingsTest(unittest.TestCase):
    def test_load_missing(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d) / "missing.json"
            with patch.object(settings_mod, "DEFAULT_PATH", tmp):
                s = settings_mod.load()
            self.assertEqual(s, settings_mod.DEFAULTS)

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d) / "s.json"
            with patch.object(settings_mod, "DEFAULT_PATH", tmp):
                settings_mod.save({"lang": "en", "sound": False, "volume": 2, "difficulty": "hard"})
                s = settings_mod.load()
            self.assertEqual(s["lang"], "en")
            self.assertFalse(s["sound"])
            self.assertEqual(s["volume"], 2)
            self.assertEqual(s["difficulty"], "hard")

    def test_load_clamps_difficulty(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d) / "s.json"
            tmp.write_text(json.dumps({"difficulty": "impossible"}))
            with patch.object(settings_mod, "DEFAULT_PATH", tmp):
                s = settings_mod.load()
            self.assertEqual(s["difficulty"], settings_mod.DEFAULTS["difficulty"])

    def test_load_sanitizes_invalid_values(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d) / "s.json"
            tmp.write_text(json.dumps({
                "lang": "fr",
                "sound": "yes",
                "volume": 99,
                "difficulty": "easy",
            }))
            with patch.object(settings_mod, "DEFAULT_PATH", tmp):
                s = settings_mod.load()
            self.assertEqual(s["lang"], settings_mod.DEFAULTS["lang"])
            self.assertEqual(s["sound"], settings_mod.DEFAULTS["sound"])
            self.assertEqual(s["volume"], 3)
            self.assertEqual(s["difficulty"], "easy")

    def test_load_rejects_bool_volume(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d) / "s.json"
            tmp.write_text(json.dumps({"volume": True}))
            with patch.object(settings_mod, "DEFAULT_PATH", tmp):
                s = settings_mod.load()
            self.assertEqual(s["volume"], settings_mod.DEFAULTS["volume"])

    def test_load_corrupt(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d) / "s.json"
            tmp.write_text("not json")
            with patch.object(settings_mod, "DEFAULT_PATH", tmp):
                s = settings_mod.load()
            self.assertEqual(s, settings_mod.DEFAULTS)

    def test_cycle_lang(self):
        self.assertEqual(settings_mod.cycle_lang("zh"), "en")
        self.assertEqual(settings_mod.cycle_lang("en"), "zh")

    def test_cycle_volume(self):
        self.assertEqual(settings_mod.cycle_volume(0), 1)
        self.assertEqual(settings_mod.cycle_volume(3), 0)

    def test_cycle_difficulty(self):
        self.assertEqual(settings_mod.cycle_difficulty("easy"), "normal")
        self.assertEqual(settings_mod.cycle_difficulty("normal"), "hard")
        self.assertEqual(settings_mod.cycle_difficulty("hard"), "easy")
        self.assertEqual(settings_mod.cycle_difficulty("xxx"), "easy")


class ScoreTest(unittest.TestCase):
    def test_load_missing(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d) / "missing.json"
            with patch.object(score_mod, "DEFAULT_PATH", tmp):
                self.assertEqual(score_mod.load(), [])

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d) / "s.json"
            with patch.object(score_mod, "DEFAULT_PATH", tmp):
                score_mod.save([{"name": "A", "score": 100}])
                loaded = score_mod.load()
            self.assertEqual(loaded, [{"name": "A", "score": 100}])

    def test_load_corrupt(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d) / "s.json"
            tmp.write_text("garbage")
            with patch.object(score_mod, "DEFAULT_PATH", tmp):
                self.assertEqual(score_mod.load(), [])

    def test_load_filters_invalid(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d) / "s.json"
            tmp.write_text(json.dumps([
                {"name": "A", "score": 1},
                {"name": "B"},
                "not a dict",
            ]))
            with patch.object(score_mod, "DEFAULT_PATH", tmp):
                loaded = score_mod.load()
            self.assertEqual(loaded, [{"name": "A", "score": 1}])

    def test_add_score_sorted_desc(self):
        out = score_mod.add_score([], {"name": "A", "score": 10})
        out = score_mod.add_score(out, {"name": "B", "score": 30})
        out = score_mod.add_score(out, {"name": "C", "score": 20})
        self.assertEqual([e["score"] for e in out], [30, 20, 10])

    def test_add_score_truncates(self):
        scores = []
        for i in range(15):
            scores = score_mod.add_score(scores, {"name": f"X{i}", "score": i})
        self.assertEqual(len(scores), score_mod.MAX_ENTRIES)
        self.assertEqual(scores[0]["score"], 14)

    def test_compute_score_win(self):
        # win + diff 5 + depth 4 → 100 + 5 + 40 = 145
        self.assertEqual(score_mod.compute_score("win", 5, 4), 145)

    def test_compute_score_loss_clamped(self):
        # loss + diff -10 + depth 0 → max(0, -10) = 0
        self.assertEqual(score_mod.compute_score("loss", -10, 0), 0)

    def test_compute_score_tie(self):
        self.assertEqual(score_mod.compute_score("tie", 0, 4), 70)


class SoundTest(unittest.TestCase):
    def test_disabled(self):
        buf = io.StringIO()
        s = Sound(enabled=False, volume=2, output=buf)
        s.click()
        self.assertEqual(buf.getvalue(), "")

    def test_zero_volume(self):
        buf = io.StringIO()
        s = Sound(enabled=True, volume=0, output=buf)
        s.click()
        self.assertEqual(buf.getvalue(), "")

    def test_click(self):
        buf = io.StringIO()
        s = Sound(enabled=True, volume=1, output=buf)
        s.click()
        self.assertEqual(buf.getvalue(), "\a")

    def test_volume_multiplier(self):
        buf = io.StringIO()
        s = Sound(enabled=True, volume=2, output=buf)
        s.win()  # 4 bells * 2 vol
        self.assertEqual(buf.getvalue(), "\a" * 8)

    def test_capture_louder(self):
        buf = io.StringIO()
        s = Sound(enabled=True, volume=1, output=buf)
        s.capture()
        self.assertEqual(buf.getvalue(), "\a\a")

    def test_volume_clamped(self):
        s = Sound(volume=99)
        self.assertEqual(s.volume, 3)
        s = Sound(volume=-1)
        self.assertEqual(s.volume, 0)


class I18nTest(unittest.TestCase):
    def test_zh_en_have_same_keys(self):
        self.assertEqual(set(STRINGS["zh"].keys()), set(STRINGS["en"].keys()))

    def test_t_format(self):
        self.assertIn("12", t("zh", "win_you", you=12, ai=0))
        self.assertIn("12", t("en", "win_you", you=12, ai=0))

    def test_t_unknown_key_returns_key(self):
        self.assertEqual(t("zh", "no_such_key"), "no_such_key")

    def test_t_unknown_lang_falls_back(self):
        self.assertEqual(t("xx", "title"), STRINGS["en"]["title"])


if __name__ == "__main__":
    unittest.main()
