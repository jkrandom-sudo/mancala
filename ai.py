"""Mancala AI — minimax with alpha-beta pruning."""
import random
from typing import Optional, Tuple

from board import Board, player_store, opponent, IllegalMove


# Heuristic weights
W_STORE_DIFF = 1.0
W_PIT_DIFF = 0.1
W_MOBILITY = 0.1


def evaluate(board: Board, player: int) -> float:
    """Heuristic: positive = good for `player`."""
    own_store = board.pits[player_store(player)]
    opp_store = board.pits[player_store(opponent(player))]
    own_pits = sum(board.pits[p] for p in (range(0, 6) if player == 0 else range(7, 13)))
    opp_pits = sum(board.pits[p] for p in (range(7, 13) if player == 0 else range(0, 6)))
    own_moves = len(board.legal_moves(player))
    opp_moves = len(board.legal_moves(opponent(player)))
    if board.is_game_over():
        # Treat sweep: simulate end-of-game scoring on a clone
        b = board.clone()
        b._sweep_remaining()
        diff = b.pits[player_store(player)] - b.pits[player_store(opponent(player))]
        # Big bonus for winning
        return diff * 100
    return (
        W_STORE_DIFF * (own_store - opp_store)
        + W_PIT_DIFF * (own_pits - opp_pits)
        + W_MOBILITY * (own_moves - opp_moves)
    )


def best_move(
    board: Board,
    depth: int = 5,
    rng: Optional[random.Random] = None,
) -> int:
    """Return the chosen pit for `board.current_player` using minimax + α-β."""
    rng = rng or random.Random()
    moves = board.legal_moves()
    if not moves:
        raise IllegalMove("no legal moves")
    me = board.current_player
    best_val = float("-inf")
    best_moves = []
    for m in moves:
        b = board.clone()
        info = b.move(m)
        if info["extra_turn"] and not b.is_game_over():
            # same player still to move
            val = _negamax(b, depth - 1, float("-inf"), float("inf"), me)
        else:
            val = -_negamax(b, depth - 1, float("-inf"), float("inf"), opponent(me))
        if val > best_val + 1e-9:
            best_val = val
            best_moves = [m]
        elif abs(val - best_val) < 1e-9:
            best_moves.append(m)
    return rng.choice(best_moves)


def _negamax(board: Board, depth: int, alpha: float, beta: float, player: int) -> float:
    if depth <= 0 or board.is_game_over():
        return evaluate(board, player)
    moves = board.legal_moves(player)
    if not moves:
        # Forfeit — terminal sweep
        b = board.clone()
        b._sweep_remaining()
        diff = b.pits[player_store(player)] - b.pits[player_store(opponent(player))]
        return diff * 100
    value = float("-inf")
    for m in moves:
        b = board.clone()
        b.current_player = player
        info = b.move(m)
        if info["extra_turn"] and not b.is_game_over():
            v = _negamax(b, depth - 1, alpha, beta, player)
        else:
            v = -_negamax(b, depth - 1, -beta, -alpha, opponent(player))
        if v > value:
            value = v
        if value > alpha:
            alpha = value
        if alpha >= beta:
            break
    return value
