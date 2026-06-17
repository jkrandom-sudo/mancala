"""Bilingual strings."""
STRINGS = {
    "zh": {
        "title": "曼卡拉 / Mancala",
        "menu_play": "P) 开始游戏",
        "menu_settings": "S) 设置",
        "menu_scores": "L) 排行榜",
        "menu_help": "H) 帮助",
        "menu_quit": "Q) 退出",
        "prompt_choice": "选择> ",
        "settings_title": "── 设置 ──",
        "settings_lang": "1) 语言: {value}",
        "settings_sound": "2) 音效: {value}",
        "settings_volume": "3) 音量: {value}",
        "settings_difficulty": "4) AI 难度: {value}",
        "settings_back": "B) 返回",
        "scores_title": "── 排行榜 (Top 10) ──",
        "scores_empty": "暂无记录。",
        "scores_row": "{rank:>2}. {name:<10} {score:>5}  result={result}  diff={diff}",
        "help_title": "── 帮助 ──",
        "help_body": (
            "曼卡拉(Kalah 变体):双方各有 6 个小坑和 1 个大坑(Store)。\n"
            "回合:从己方小坑(标号 1-6)取出全部种子,逆时针方向每坑放 1 颗。\n"
            "  规则:经过自家大坑放 1 颗,经过对方大坑直接跳过。\n"
            "  连击:最后一颗落入己方大坑,可再走一次。\n"
            "  捕获:最后一颗落入己方空小坑,且对面对应坑非空,则吃掉两侧种子。\n"
            "结束:任意一方所有小坑全空,另一方剩余种子归其大坑。大坑多者胜。\n"
            "命令:输入 1-6 选择小坑,u 撤销, h 提示, r 重置, q 放弃。"
        ),
        "press_enter": "回车继续...",
        "round_start": "── 新一局 (你 vs AI [{lvl}]) ──",
        "your_turn": "你的回合 (1-6, u/h/r/q):",
        "ai_turn": "AI 思考中...",
        "ai_played": "AI 选择小坑 {pit}{extra}{cap}",
        "extra_label": " (再走一次)",
        "capture_label": " — 吃掉 {n} 颗",
        "you_captured": "你吃掉了 {n} 颗种子!",
        "extra_turn_you": "再走一次!",
        "invalid_pit": "无效的坑号。请输入 1-6。",
        "illegal_move": "非法移动:{reason}",
        "no_history": "没有可撤销的步骤。",
        "hint_line": "提示:从坑 {pit} 出发。",
        "reset_done": "已重置当前对局。",
        "win_you": "你赢了!最终 {you} : {ai}",
        "win_ai": "AI 赢了。最终 {you} : {ai}",
        "win_tie": "平局。最终 {you} : {ai}",
        "round_done": "完成!得分 {score}。",
        "save_name": "输入名字保存(回车跳过): ",
        "on": "开",
        "off": "关",
        "lang_zh": "中文",
        "lang_en": "English",
        "lvl_easy": "简单",
        "lvl_normal": "普通",
        "lvl_hard": "困难",
        "result_win": "胜",
        "result_loss": "负",
        "result_tie": "平",
        "bye": "再见!",
        "unknown": "未知选择。",
    },
    "en": {
        "title": "Mancala",
        "menu_play": "P) Play",
        "menu_settings": "S) Settings",
        "menu_scores": "L) Leaderboard",
        "menu_help": "H) Help",
        "menu_quit": "Q) Quit",
        "prompt_choice": "Choice> ",
        "settings_title": "-- Settings --",
        "settings_lang": "1) Language: {value}",
        "settings_sound": "2) Sound: {value}",
        "settings_volume": "3) Volume: {value}",
        "settings_difficulty": "4) AI Level: {value}",
        "settings_back": "B) Back",
        "scores_title": "-- Leaderboard (Top 10) --",
        "scores_empty": "No scores yet.",
        "scores_row": "{rank:>2}. {name:<10} {score:>5}  result={result}  diff={diff}",
        "help_title": "-- Help --",
        "help_body": (
            "Mancala (Kalah variant): each side has 6 small pits and 1 store.\n"
            "Turn: pick a pit on your row (numbered 1-6), sow seeds counter-clockwise,\n"
            "  one per pit. Drop one in your own store; SKIP the opponent's store.\n"
            "  Extra turn: if last seed lands in your own store.\n"
            "  Capture: if last seed lands in YOUR empty pit and the opposite pit\n"
            "           has seeds, capture both into your store.\n"
            "End: when one side's pits are all empty; the other side's remaining\n"
            "     seeds go to that side's store. Larger store wins.\n"
            "Commands: 1-6 choose pit, u undo, h hint, r reset, q quit."
        ),
        "press_enter": "Press Enter to continue...",
        "round_start": "-- New round (You vs AI [{lvl}]) --",
        "your_turn": "Your turn (1-6, u/h/r/q):",
        "ai_turn": "AI thinking...",
        "ai_played": "AI chose pit {pit}{extra}{cap}",
        "extra_label": " (extra turn)",
        "capture_label": " — captured {n}",
        "you_captured": "You captured {n} seeds!",
        "extra_turn_you": "Extra turn!",
        "invalid_pit": "Bad pit. Enter 1-6.",
        "illegal_move": "Illegal: {reason}",
        "no_history": "Nothing to undo.",
        "hint_line": "Hint: try pit {pit}.",
        "reset_done": "Game reset.",
        "win_you": "You win! Final {you} : {ai}",
        "win_ai": "AI wins. Final {you} : {ai}",
        "win_tie": "Tie. Final {you} : {ai}",
        "round_done": "Score {score}.",
        "save_name": "Enter name to save (blank to skip): ",
        "on": "On",
        "off": "Off",
        "lang_zh": "Chinese",
        "lang_en": "English",
        "lvl_easy": "Easy",
        "lvl_normal": "Normal",
        "lvl_hard": "Hard",
        "result_win": "WIN",
        "result_loss": "LOSS",
        "result_tie": "TIE",
        "bye": "Bye!",
        "unknown": "Unknown choice.",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    table = STRINGS.get(lang, STRINGS["en"])
    val = table.get(key, key)
    if isinstance(val, str) and kwargs:
        try:
            return val.format(**kwargs)
        except (KeyError, IndexError):
            return val
    return val
