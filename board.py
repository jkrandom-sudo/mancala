"""Mancala (Kalah) board state and rules.

Layout (Kalah variant):
- 2 players: 0 (south, bottom) and 1 (north, top)
- 6 small pits per player + 1 store ("kalah") per player
- Internal pit indices:
    0..5  = player 0's small pits, left-to-right (south side)
    6     = player 0's store
    7..12 = player 1's small pits, left-to-right from player 1's perspective
            i.e. indices 7,8,9,10,11,12 are physically right-to-left along the top
    13    = player 1's store
- Sowing: counter-clockwise (0→1→2→...→6→7→...→12→ skip 13 →0).
  A player skips the OPPONENT's store.
- Extra turn: if last seed lands in own store.
- Capture: if last seed lands in own EMPTY pit and opposite pit non-empty,
  capture both into own store.
- End: when one side's small pits are all empty. Remaining seeds on the
  other side go to that side's store.
"""
from typing import List, Optional, Tuple


PITS_PER_SIDE = 6
INITIAL_SEEDS = 4
TOTAL_PITS = 14  # 6 + 1 + 6 + 1
STORES = (6, 13)


class IllegalMove(Exception):
    """Raised when a move is invalid. code is a translatable error key."""
    def __init__(self, code: str, **fmt):
        self.code = code
        self.fmt = fmt
        super().__init__(code)

    def __str__(self):
        return self.code


def opposite_pit(pit: int) -> int:
    """Return the pit physically opposite `pit` across the board."""
    if pit == 6 or pit == 13:
        raise ValueError("stores have no opposite")
    if 0 <= pit <= 5:
        return 12 - pit  # 0<->12, 1<->11, 2<->10, 3<->9, 4<->8, 5<->7
    if 7 <= pit <= 12:
        return 12 - pit
    raise IllegalMove("err_pit_out_of_range", pit=pit)


def player_pits(player: int) -> range:
    if player == 0:
        return range(0, 6)
    if player == 1:
        return range(7, 13)
    raise ValueError(f"bad player {player}")


def player_store(player: int) -> int:
    if player == 0:
        return 6
    if player == 1:
        return 13
    raise ValueError(f"bad player {player}")


def opponent(player: int) -> int:
    return 1 - player


class Board:
    def __init__(self):
        self.pits: List[int] = [INITIAL_SEEDS] * TOTAL_PITS
        self.pits[6] = 0
        self.pits[13] = 0
        self.current_player: int = 0
        self.last_capture: int = 0  # seeds captured on last move (for UI feedback)
        self.last_extra_turn: bool = False
        self.history: List[Tuple] = []

    def clone(self) -> "Board":
        b = Board()
        b.pits = list(self.pits)
        b.current_player = self.current_player
        b.last_capture = self.last_capture
        b.last_extra_turn = self.last_extra_turn
        # don't copy history — clones are for AI simulation
        return b

    def legal_moves(self, player: Optional[int] = None) -> List[int]:
        if player is None:
            player = self.current_player
        return [p for p in player_pits(player) if self.pits[p] > 0]

    def is_game_over(self) -> bool:
        side0_empty = all(self.pits[p] == 0 for p in player_pits(0))
        side1_empty = all(self.pits[p] == 0 for p in player_pits(1))
        return side0_empty or side1_empty

    def _sweep_remaining(self) -> None:
        """At game end, each side's remaining seeds go to that side's store."""
        for p in player_pits(0):
            self.pits[6] += self.pits[p]
            self.pits[p] = 0
        for p in player_pits(1):
            self.pits[13] += self.pits[p]
            self.pits[p] = 0

    def winner(self) -> Optional[int]:
        """Return 0, 1, or None for tie. Only meaningful after is_game_over() and finalize."""
        if self.pits[6] > self.pits[13]:
            return 0
        if self.pits[13] > self.pits[6]:
            return 1
        return None

    def move(self, pit: int) -> dict:
        """Sow seeds from `pit` according to Kalah rules.

        Returns a dict with: extra_turn (bool), captured (int), game_over (bool),
        last_pit (int).
        Raises IllegalMove for: out-of-range, store-pit, empty-pit,
        wrong-side-pit, or if game already over.
        """
        if self.is_game_over():
            raise IllegalMove("err_game_over")
        if not (0 <= pit < TOTAL_PITS):
            raise IllegalMove("err_pit_out_of_range")
        if pit in STORES:
            raise IllegalMove("err_cannot_pick_from_store")
        if pit not in player_pits(self.current_player):
            raise IllegalMove("err_not_your_pit")
        seeds = self.pits[pit]
        if seeds == 0:
            raise IllegalMove("err_pit_is_empty")

        # Snapshot for undo
        snapshot = (list(self.pits), self.current_player)

        own_store = player_store(self.current_player)
        opp_store = player_store(opponent(self.current_player))

        self.pits[pit] = 0
        idx = pit
        while seeds > 0:
            idx = (idx + 1) % TOTAL_PITS
            if idx == opp_store:
                continue
            self.pits[idx] += 1
            seeds -= 1

        last_pit = idx
        captured = 0
        extra_turn = False

        # Capture: last seed in own empty (now == 1) small pit + opposite has seeds
        if last_pit in player_pits(self.current_player) and self.pits[last_pit] == 1:
            opp = opposite_pit(last_pit)
            if self.pits[opp] > 0:
                captured = self.pits[opp] + 1
                self.pits[own_store] += captured
                self.pits[opp] = 0
                self.pits[last_pit] = 0

        # Extra turn if landed in own store
        if last_pit == own_store:
            extra_turn = True

        self.last_capture = captured
        self.last_extra_turn = extra_turn
        self.history.append(snapshot)

        # If game ended (one side empty), sweep remaining
        game_over = False
        if self.is_game_over():
            self._sweep_remaining()
            game_over = True
        elif not extra_turn:
            self.current_player = opponent(self.current_player)

        return {
            "extra_turn": extra_turn,
            "captured": captured,
            "game_over": game_over,
            "last_pit": last_pit,
        }

    def undo(self) -> bool:
        if not self.history:
            return False
        pits, player = self.history.pop()
        self.pits = list(pits)
        self.current_player = player
        self.last_capture = 0
        self.last_extra_turn = False
        return True

    def state_tuple(self) -> Tuple:
        return tuple(self.pits) + (self.current_player,)

    def reset(self) -> None:
        self.__init__()
