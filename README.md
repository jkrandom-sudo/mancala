# 曼卡拉 / Mancala

A pure-Python (stdlib only) console implementation of **Mancala (Kalah variant)** —
the classic 3000-year-old sowing/capture board game.  Play against a minimax+α-β
AI with three difficulty levels.  Bilingual UI (中文 / English), persistent
settings, top-10 leaderboard, optimal-move hint, undo/reset, terminal-bell SFX.

> Goal: capture more seeds than the AI by sowing strategically. Larger store wins.

## Rules (Kalah variant)

- 2 players, 6 small pits per side + 1 store ("kalah") per side.
- 4 seeds in each small pit at start (48 total).
- On your turn, pick one of YOUR small pits and sow its seeds **counter-clockwise**,
  one per pit. Drop one in YOUR store; **skip** the opponent's store.
- **Extra turn**: if the last seed lands in your own store.
- **Capture**: if the last seed lands in YOUR previously-empty pit, capture
  both that seed and all seeds from the opposite pit into your store.
- **Game ends** when one side's pits are all empty. Remaining seeds on the
  other side go to that side's store. Larger store wins.

## Features

- Minimax + alpha-beta AI at three difficulty levels (easy/normal/hard)
- Optimal-move hint (uses the AI itself)
- Undo (rolls back through AI moves), reset, quit
- Bilingual: 中文 / English (toggle in Settings → 1)
- Persistent settings  → `~/.mancala_settings.json`
- Persistent top-10 leaderboard → `~/.mancala_scores.json`
- Sound on/off + 4-level volume (terminal bell `\a`)
- Pure Python 3 stdlib — no third-party packages

## Quickstart

```bash
git clone https://github.com/jkrandom-sudo/mancala.git
cd mancala
python3 game.py
```

## In-game commands

At your turn prompt:

| Input  | Effect                                       |
|--------|----------------------------------------------|
| `1`-`6`| Pick small pit (left-to-right on YOUR row)   |
| `u`    | Undo last move (back to your turn)           |
| `h`    | Hint — show recommended pit                  |
| `r`    | Reset current game                           |
| `q`    | Abandon round, return to menu                |

## Board layout

```
       12  11  10   9   8   7        ← AI's pits
     +------------------------------+
[AI ]|   3   3   3   3   3   3   |[ You ]
     +------------------------------+
     |   3   3   3   3   3   3   |
        1   2   3   4   5   6        ← your pits
```

Counter-clockwise sowing:  `1 → 2 → 3 → 4 → 5 → 6 → [your store] → 12 → 11 → 10 → 9 → 8 → 7 → 1 …`

## Scoring

```
score = base + diff + depth × 10
   where base = 100 (win) / 30 (tie) / 0 (loss)
         diff = your_store − ai_store    (signed)
         depth = AI search depth (easy=2, normal=4, hard=7)
   clamped to ≥ 0
```

## Project layout

```
mancala/
├── game.py            # menu + round loop
├── board.py           # Board class (state, sowing, capture, end detection)
├── ai.py              # minimax + α-β + heuristic eval
├── i18n.py            # zh / en strings + t() helper
├── settings.py        # JSON settings persistence
├── score.py           # JSON leaderboard persistence
├── sound.py           # terminal-bell SFX
├── tests/
│   ├── test_board.py
│   ├── test_ai.py
│   ├── test_modules.py
│   ├── test_game.py
│   └── run_tests.py
└── README.md
```

## Running tests

```bash
python3 tests/run_tests.py
```

82 tests cover sowing, opponent-store skipping, capture, extra-turn, end-of-game
sweep, undo/reset, AI legality and termination, settings/score persistence,
sound, i18n fallbacks, and the menu / round loop flow via a scripted-input helper.

## License

MIT
