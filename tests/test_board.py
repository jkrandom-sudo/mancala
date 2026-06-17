"""Tests for board state and rules."""
import unittest

from board import (
    Board,
    IllegalMove,
    INITIAL_SEEDS,
    PITS_PER_SIDE,
    opposite_pit,
    player_pits,
    player_store,
    opponent,
)


class HelpersTest(unittest.TestCase):
    def test_opposite(self):
        self.assertEqual(opposite_pit(0), 12)
        self.assertEqual(opposite_pit(5), 7)
        self.assertEqual(opposite_pit(7), 5)
        self.assertEqual(opposite_pit(12), 0)

    def test_opposite_store_raises(self):
        with self.assertRaises(ValueError):
            opposite_pit(6)
        with self.assertRaises(ValueError):
            opposite_pit(13)

    def test_player_pits(self):
        self.assertEqual(list(player_pits(0)), [0, 1, 2, 3, 4, 5])
        self.assertEqual(list(player_pits(1)), [7, 8, 9, 10, 11, 12])

    def test_player_store(self):
        self.assertEqual(player_store(0), 6)
        self.assertEqual(player_store(1), 13)

    def test_opponent(self):
        self.assertEqual(opponent(0), 1)
        self.assertEqual(opponent(1), 0)


class BoardSetupTest(unittest.TestCase):
    def test_initial(self):
        b = Board()
        for p in range(0, 6):
            self.assertEqual(b.pits[p], INITIAL_SEEDS)
        for p in range(7, 13):
            self.assertEqual(b.pits[p], INITIAL_SEEDS)
        self.assertEqual(b.pits[6], 0)
        self.assertEqual(b.pits[13], 0)
        self.assertEqual(b.current_player, 0)
        self.assertFalse(b.is_game_over())

    def test_legal_moves(self):
        b = Board()
        self.assertEqual(b.legal_moves(), [0, 1, 2, 3, 4, 5])
        self.assertEqual(b.legal_moves(1), [7, 8, 9, 10, 11, 12])

    def test_legal_moves_skip_empty(self):
        b = Board()
        b.pits[2] = 0
        self.assertEqual(b.legal_moves(), [0, 1, 3, 4, 5])

    def test_clone_independent(self):
        b = Board()
        c = b.clone()
        b.pits[0] = 99
        self.assertEqual(c.pits[0], INITIAL_SEEDS)


class MoveTest(unittest.TestCase):
    def test_simple_sow(self):
        b = Board()
        # pit 0 has 4, sows to 1,2,3,4
        info = b.move(0)
        self.assertEqual(b.pits[0], 0)
        self.assertEqual(b.pits[1], 5)
        self.assertEqual(b.pits[2], 5)
        self.assertEqual(b.pits[3], 5)
        self.assertEqual(b.pits[4], 5)
        self.assertEqual(b.pits[5], 4)  # untouched
        self.assertFalse(info["extra_turn"])
        self.assertEqual(info["captured"], 0)
        self.assertEqual(b.current_player, 1)  # turn switched

    def test_extra_turn_when_landing_in_own_store(self):
        b = Board()
        # Pit 2 has 4 → sows to 3,4,5,6 (own store) → extra turn
        info = b.move(2)
        self.assertEqual(b.pits[6], 1)
        self.assertTrue(info["extra_turn"])
        self.assertEqual(b.current_player, 0)  # still player 0

    def test_skip_opponent_store(self):
        b = Board()
        # Set pit 5 to 9 seeds. Sowing: 6,7,8,9,10,11,12,skip-13,0,1 = 9 drops.
        b.pits[5] = 9
        info = b.move(5)
        self.assertEqual(b.pits[5], 0)
        self.assertEqual(b.pits[6], 1)
        for p in range(7, 13):
            self.assertEqual(b.pits[p], INITIAL_SEEDS + 1)
        self.assertEqual(b.pits[13], 0)  # NEVER touched
        self.assertEqual(b.pits[0], INITIAL_SEEDS + 1)  # 4 + 1 = 5
        self.assertEqual(b.pits[1], INITIAL_SEEDS + 1)  # 4 + 1 = 5
        self.assertEqual(info["last_pit"], 1)

    def test_capture(self):
        b = Board()
        # Set pit 1 to 1 seed, pit 2 to 0 (last lands in 2), opposite (10) has seeds
        b.pits[0] = 0
        b.pits[1] = 1
        b.pits[2] = 0
        b.pits[10] = 5
        info = b.move(1)
        # 1 seed sown to pit 2 — own empty pit, capture pit 10's 5 seeds + the seed = 6
        self.assertEqual(info["captured"], 6)
        self.assertEqual(b.pits[2], 0)
        self.assertEqual(b.pits[10], 0)
        self.assertEqual(b.pits[6], 6)

    def test_no_capture_on_opp_side(self):
        b = Board()
        # Configure: last seed lands in opponent's empty pit
        b.pits[5] = 5  # sows to 6,7,8,9,10
        b.pits[10] = 0
        info = b.move(5)
        # Last lands in 10 (opponent side). No capture for current player.
        self.assertEqual(info["captured"], 0)
        self.assertEqual(b.pits[10], 1)

    def test_no_capture_when_opposite_empty(self):
        b = Board()
        b.pits[0] = 0
        b.pits[1] = 1  # sows 1 seed to pit 2
        b.pits[2] = 0
        b.pits[10] = 0  # opposite of 2
        info = b.move(1)
        self.assertEqual(info["captured"], 0)
        self.assertEqual(b.pits[2], 1)  # seed stays

    def test_illegal_pit_out_of_range(self):
        b = Board()
        with self.assertRaises(IllegalMove):
            b.move(99)

    def test_illegal_store_pick(self):
        b = Board()
        with self.assertRaises(IllegalMove):
            b.move(6)

    def test_illegal_wrong_side(self):
        b = Board()
        # Player 0's turn — picking from player 1 row
        with self.assertRaises(IllegalMove):
            b.move(7)

    def test_illegal_empty_pit(self):
        b = Board()
        b.pits[0] = 0
        with self.assertRaises(IllegalMove):
            b.move(0)

    def test_undo(self):
        b = Board()
        before = list(b.pits)
        b.move(0)
        self.assertNotEqual(b.pits, before)
        self.assertTrue(b.undo())
        self.assertEqual(b.pits, before)
        self.assertEqual(b.current_player, 0)

    def test_undo_empty(self):
        b = Board()
        self.assertFalse(b.undo())

    def test_reset(self):
        b = Board()
        b.move(0)
        b.reset()
        self.assertEqual(b.pits[6], 0)
        self.assertEqual(b.current_player, 0)
        self.assertEqual(b.history, [])


class GameOverTest(unittest.TestCase):
    def test_is_over_one_side_empty(self):
        b = Board()
        for p in range(0, 6):
            b.pits[p] = 0
        self.assertTrue(b.is_game_over())

    def test_sweep_at_end(self):
        b = Board()
        # Player 0 about to empty their side; one seed in pit 5
        for p in range(0, 6):
            b.pits[p] = 0
        b.pits[5] = 1
        # Player 1 still has all their seeds
        info = b.move(5)
        # Sowing 1 seed from 5 → goes to 6 (own store) → game ends because side 0 now empty
        self.assertTrue(info["game_over"])
        self.assertEqual(b.pits[6], 1)
        # Player 1's seeds should have been swept to their store
        for p in range(7, 13):
            self.assertEqual(b.pits[p], 0)
        self.assertEqual(b.pits[13], INITIAL_SEEDS * PITS_PER_SIDE)

    def test_winner(self):
        b = Board()
        b.pits[6] = 30
        b.pits[13] = 18
        self.assertEqual(b.winner(), 0)
        b.pits[6] = 10
        self.assertEqual(b.winner(), 1)
        b.pits[6] = 18
        self.assertIsNone(b.winner())


if __name__ == "__main__":
    unittest.main()
