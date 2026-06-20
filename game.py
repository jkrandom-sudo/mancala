"""Mancala — TUI menu + round loop."""
import random
import sys
from typing import Callable, Optional

from board import Board, IllegalMove, player_pits, player_store
from ai import best_move
from i18n import t
import score as score_mod
import settings as settings_mod
from sound import Sound


HUMAN = 0
AI = 1


class QuitGame(Exception):
    pass


def write(output, *parts) -> None:
    for p in parts:
        output.write(str(p))
    output.write("\n")
    output.flush()


def render_board(board: Board, lang: str) -> str:
    """ASCII board.

    Top row (player 1): pits 12..7 left-to-right (their perspective is right-to-left
    along the top of the physical board, so reading L→R for the human viewer = 12,11,..7).
    """
    p = board.pits
    # top row: ai pits 12,11,10,9,8,7
    top = "  ".join(f"{p[i]:>2}" for i in (12, 11, 10, 9, 8, 7))
    # stores: left = player1 (AI=13), right = player0 (you=6)
    left_store = f"[{p[13]:>2}]"
    right_store = f"[{p[6]:>2}]"
    # bottom row: human pits 0..5
    bot = "  ".join(f"{p[i]:>2}" for i in (0, 1, 2, 3, 4, 5))

    lines = []
    lines.append("       12  11  10   9   8   7   ")
    lines.append(f"     +" + "-" * 30 + "+")
    lines.append(f"{left_store}|  {top}  |{right_store}")
    lines.append(f"     +" + "-" * 30 + "+")
    lines.append(f"     |  {bot}  |")
    lines.append("        1   2   3   4   5   6   ")
    lines.append(f"     (AI: {p[13]}    You: {p[6]})")
    return "\n".join(lines)


def parse_pit(text: str) -> Optional[int]:
    """Parse user input '1'-'6' to internal pit index 0-5."""
    s = text.strip()
    if not s.isdigit():
        return None
    n = int(s)
    if 1 <= n <= 6:
        return n - 1
    return None


def show(output, board: Board, lang: str) -> None:
    write(output, render_board(board, lang))


def play_round(
    settings: dict,
    sound: Sound,
    input_func: Callable[[str], str],
    output,
    rng: Optional[random.Random] = None,
) -> Optional[dict]:
    rng = rng or random.Random()
    lang = settings["lang"]
    diff = settings["difficulty"]
    depth = settings_mod.DIFFICULTY[diff]["depth"]
    board = Board()
    write(output, t(lang, "round_start", lvl=t(lang, settings_mod.DIFFICULTY[diff]["label"])))

    while not board.is_game_over():
        show(output, board, lang)
        if board.current_player == HUMAN:
            try:
                raw = input_func(t(lang, "your_turn") + " ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                raise QuitGame()
            if not raw:
                continue
            if raw == "q":
                return None
            if raw == "r":
                board.reset()
                sound.reset()
                write(output, t(lang, "reset_done"))
                continue
            if raw == "u":
                # Undo until it's the human's turn again (one or two pops)
                if not board.history:
                    write(output, t(lang, "no_history"))
                    continue
                board.undo()
                # If after undo it's the AI's turn, undo once more
                while board.history and board.current_player != HUMAN:
                    board.undo()
                sound.undo()
                continue
            if raw == "h":
                m = best_move(board, depth=max(2, depth), rng=rng)
                sound.hint()
                write(output, t(lang, "hint_line", pit=m + 1))
                continue
            pit = parse_pit(raw)
            if pit is None:
                write(output, t(lang, "invalid_pit"))
                continue
            try:
                info = board.move(pit)
            except IllegalMove as e:
                reason = t(lang, e.code, **e.fmt) if e.fmt else t(lang, e.code)
                write(output, t(lang, "illegal_move", reason=reason))
                continue
            sound.click()
            if info["captured"] > 0:
                sound.capture()
                write(output, t(lang, "you_captured", n=info["captured"]))
            if info["extra_turn"] and not info["game_over"]:
                sound.extra()
                write(output, t(lang, "extra_turn_you"))
        else:
            write(output, t(lang, "ai_turn"))
            try:
                m = best_move(board, depth=depth, rng=rng)
            except IllegalMove:
                break
            info = board.move(m)
            extra = t(lang, "extra_label") if info["extra_turn"] and not info["game_over"] else ""
            cap = t(lang, "capture_label", n=info["captured"]) if info["captured"] > 0 else ""
            write(output, t(lang, "ai_played", pit=m - 6, extra=extra, cap=cap))
            sound.click()

    show(output, board, lang)
    you, ai_score = board.pits[6], board.pits[13]
    if you > ai_score:
        write(output, t(lang, "win_you", you=you, ai=ai_score))
        sound.win()
        result = "win"
    elif ai_score > you:
        write(output, t(lang, "win_ai", you=you, ai=ai_score))
        sound.lose()
        result = "loss"
    else:
        write(output, t(lang, "win_tie", you=you, ai=ai_score))
        result = "tie"
    diff_score = you - ai_score
    sc = score_mod.compute_score(result, diff_score, depth)
    write(output, t(lang, "round_done", score=sc))
    return {
        "won": result == "win",
        "result": result,
        "score": sc,
        "diff": diff_score,
        "difficulty": diff,
    }


def show_scores(input_func, output, lang: str) -> None:
    scores = score_mod.load()
    write(output, t(lang, "scores_title"))
    if not scores:
        write(output, t(lang, "scores_empty"))
    else:
        for i, e in enumerate(scores, 1):
            r = e.get("result", "")
            r_label = {"win": t(lang, "result_win"), "loss": t(lang, "result_loss"),
                       "tie": t(lang, "result_tie")}.get(r, r)
            write(output, t(
                lang, "scores_row",
                rank=i,
                name=e.get("name", "?"),
                score=e.get("score", 0),
                result=r_label,
                diff=e.get("diff", 0),
            ))
    try:
        input_func(t(lang, "press_enter"))
    except (EOFError, KeyboardInterrupt):
        pass


def show_help(input_func, output, lang: str) -> None:
    write(output, t(lang, "help_title"))
    write(output, t(lang, "help_body"))
    try:
        input_func(t(lang, "press_enter"))
    except (EOFError, KeyboardInterrupt):
        pass


def settings_menu(settings: dict, sound: Sound, input_func, output) -> None:
    while True:
        lang = settings["lang"]
        sound_label = t(lang, "on" if settings["sound"] else "off")
        diff_label = t(lang, settings_mod.DIFFICULTY[settings["difficulty"]]["label"])
        write(output, t(lang, "settings_title"))
        write(output, t(lang, "settings_lang",
                        value=t(lang, "lang_zh") if lang == "zh" else t(lang, "lang_en")))
        write(output, t(lang, "settings_sound", value=sound_label))
        write(output, t(lang, "settings_volume", value=settings["volume"]))
        write(output, t(lang, "settings_difficulty", value=diff_label))
        write(output, t(lang, "settings_back"))
        try:
            choice = input_func(t(lang, "prompt_choice")).strip().lower()
        except (EOFError, KeyboardInterrupt):
            return
        if choice == "1":
            settings["lang"] = settings_mod.cycle_lang(settings["lang"])
        elif choice == "2":
            settings["sound"] = not settings["sound"]
            sound.enabled = settings["sound"]
        elif choice == "3":
            settings["volume"] = settings_mod.cycle_volume(settings["volume"])
            sound.volume = settings["volume"]
        elif choice == "4":
            settings["difficulty"] = settings_mod.cycle_difficulty(settings["difficulty"])
        elif choice == "b":
            settings_mod.save(settings)
            return
        else:
            write(output, t(lang, "unknown"))


def main_menu(
    input_func: Callable[[str], str] = input,
    output=sys.stdout,
    rng: Optional[random.Random] = None,
) -> None:
    settings = settings_mod.load()
    sound = Sound(enabled=settings["sound"], volume=settings["volume"], output=output)
    rng = rng or random.Random()

    while True:
        lang = settings["lang"]
        write(output, "")
        write(output, t(lang, "title"))
        write(output, t(lang, "menu_play"))
        write(output, t(lang, "menu_settings"))
        write(output, t(lang, "menu_scores"))
        write(output, t(lang, "menu_help"))
        write(output, t(lang, "menu_quit"))
        try:
            choice = input_func(t(lang, "prompt_choice")).strip().lower()
        except (EOFError, KeyboardInterrupt):
            write(output, t(lang, "bye"))
            return
        if choice == "p":
            try:
                result = play_round(settings, sound, input_func, output, rng=rng)
            except QuitGame:
                write(output, t(lang, "bye"))
                return
            if result is not None:
                try:
                    name = input_func(t(lang, "save_name")).strip()
                except (EOFError, KeyboardInterrupt):
                    name = ""
                if name:
                    scores = score_mod.load()
                    entry = {"name": name[:10], **result}
                    scores = score_mod.add_score(scores, entry)
                    score_mod.save(scores)
        elif choice == "s":
            settings_menu(settings, sound, input_func, output)
        elif choice == "l":
            show_scores(input_func, output, lang)
        elif choice == "h":
            show_help(input_func, output, lang)
        elif choice == "q":
            write(output, t(lang, "bye"))
            return
        else:
            write(output, t(lang, "unknown"))


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print()
