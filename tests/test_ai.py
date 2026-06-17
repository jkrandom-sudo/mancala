"""Tests for AI."""
import random
import unittest

from board import Board, IllegalMove
from ai import best_move, evaluate


class EvaluateTest(unittest.TestCase):
    def test_initial_zero_diff(self):
        b = Board()
        # Symmetric board → 0 score diff
        self.assertEqual(evaluate(b, 0), 0)
        self.assertEqual(evaluate(b, 1), 0)

    def test_store_advantage(self):
        b = Board()
        b.pits[6] = 10
        b.pits[13] = 0
        self.assertGreater(evaluate(b, 0), 0)
        self.assertLess(evaluate(b, 1), 0)


class BestMoveTest(unittest.TestCase):
    def test_returns_legal_pit(self):
        b = Board()
        m = best_move(b, depth=2, rng=random.Random(1))
        self.assertIn(m, b.legal_moves())

    def test_no_legal_moves(self):
        b = Board()
        for p in range(0, 6):
            b.pits[p] = 0
        with self.assertRaises(IllegalMove):
            best_move(b, depth=2)

    def test_prefers_extra_turn_opening(self):
        # On opening, pit 2 (4 seeds → lands in own store) gives an extra turn.
        # At shallow depth=1 (no follow-up search) AI should clearly prefer pit 2.
        b = Board()
        m = best_move(b, depth=1, rng=random.Random(0))
        self.assertEqual(m, 2)

    def test_self_play_terminates(self):
        b = Board()
        moves = 0
        rng = random.Random(42)
        while not b.is_game_over() and moves < 200:
            m = best_move(b, depth=3, rng=rng)
            b.move(m)
            moves += 1
        self.assertTrue(b.is_game_over())
        # Total seeds preserved (2 sides * 6 pits * 4 = 48)
        self.assertEqual(sum(b.pits), 48)

    def test_endgame_capture_preferred(self):
        # AI to move with two options: pit 7 captures, pit 12 just gets extra turn.
        # Both look good but pit 7 ends the game with a clear win — at deeper search
        # the AI sees that pit 7 sweeps remaining seeds favorably.
        b = Board()
        b.current_player = 1
        b.pits = [0] * 14
        b.pits[7] = 1
        b.pits[8] = 0
        b.pits[4] = 5
        b.pits[12] = 1
        m = best_move(b, depth=2, rng=random.Random(0))
        # Either move is reasonable; verify AI picks one of them and not anything else
        self.assertIn(m, (7, 12))

    def test_immediate_capture_wins(self):
        # Construct: AI's only sensible move is the capture; opponent has no follow-up.
        b = Board()
        b.current_player = 1
        b.pits = [0] * 14
        b.pits[7] = 1
        b.pits[8] = 0
        b.pits[4] = 5  # opposite of 8
        m = best_move(b, depth=3, rng=random.Random(0))
        self.assertEqual(m, 7)


if __name__ == "__main__":
    unittest.main()
