import curses
import dataclasses
import enum
import io
import pathlib
import random
import typing

COLEMAK = list("qqwwffppggjjlluuyy;:[{]}aarrssttddhhnneeiioo'\"zzxxccvvbbkkmm,<.>/?")
QWERTY = list("qqwweerrttyyuuiioopp[{]}aassddffgghhjjkkll;:'\"zzxxccvvbbnnmm,<.>/?")
SCRIPT_DIR = pathlib.Path(__file__).parent
MAX_W = 10
"""Minimum: 2"""


class CharState(enum.Enum):
    CORRECT = enum.auto()
    INCORRECT = enum.auto()
    DEFAULT = enum.auto()


STATE_COLORS = {
    CharState.CORRECT: 1,
    CharState.INCORRECT: 2,
    CharState.DEFAULT: 3,
}


@dataclasses.dataclass
class Char:
    char: str
    typed: str
    state: CharState


def get_index(arr: list, item: object) -> int | None:
    try:
        return arr.index(item)
    except ValueError:
        return None


def convert_char(char: str, target_layout: list[str], emulate_layout: list[str]) -> str:
    ei = get_index(target_layout, char)
    if ei:
        return emulate_layout[ei]
    return char


def get_words() -> str:
    with open(SCRIPT_DIR / "words/two-hundred.txt") as file:
        return " ".join(random.choices(file.read().split(), k=20))  # noqa:S311


def lrgst_k_sp_ss(k: int, arr: list[Char]) -> str:
    """Find largest space-separated substring."""
    s = io.StringIO()
    cc = 0
    lrg = ""

    for c in arr:
        s.write(c.char)
        if c.char == " ":
            if cc == k:
                cc = 0
                _s = s.getvalue()
                if len(_s) > len(lrg):
                    lrg = _s
                s.seek(0)
                s.truncate(0)
            else:
                cc += 1

    return lrg


def get_char_arr() -> list[Char]:
    return [Char(c, typed=c, state=CharState.DEFAULT) for c in get_words()]


# https://stackoverflow.com/a/66002772/22818367
def _cache(fun: typing.Callable) -> typing.Callable:  # type: ignore
    _cache.cache_ = {}  # type: ignore

    def inner(x: int, y: int, *args: list) -> int:  # type: ignore
        if (x, y) not in _cache.cache_:  # type: ignore
            _cache.cache_[(x, y)] = fun(x, y, *args)  # type: ignore
        return _cache.cache_[(x, y)]  # type: ignore

    return inner


@_cache
def _calc_ss(y: int, x: int, ss: int, chars: list[Char], max_w: int) -> tuple[int, int]:
    while (x - ((x // 2 - ss // 2) + ss)) < 10:
        max_w -= 1
        if max_w <= 2:
            max_w = 2
            break
        ss = len(lrgst_k_sp_ss(max_w - 1, chars))
    return max_w, ss


def printer(_cur: int, chars: list[Char], stdscr: curses.window) -> None:
    # FIXME: errors when text is out of bound
    stdscr.clear()
    max_w = MAX_W
    ss = len(lrgst_k_sp_ss(max_w, chars))

    y, x = stdscr.getmaxyx()
    max_w, ss = _calc_ss(y, x, ss, chars, max_w)

    ax = x // 2 - ss // 2
    ax = ax if ax > 0 else 0
    ay = y // 2

    cx, cy = 0, 0
    cc = ccc = 0
    pl = 0

    stdscr.move(ay, ax)

    for c in chars:
        col = STATE_COLORS[c.state]

        if c.state is CharState.INCORRECT and c.typed == " ":
            col = 4

        stdscr.addch(c.typed, curses.color_pair(col))

        if c.state != CharState.DEFAULT:
            cx += 1
            if c.char == " ":
                if ccc == max_w - 1:
                    cy += 1
                    cx = 0
                    ccc = 0
                else:
                    ccc += 1

        if c.char == " ":
            if cc == max_w - 1:
                cc = 0
                pl += 1
                stdscr.move(ay + pl, ax)
            else:
                cc += 1

    stdscr.move(ay + cy, ax + cx)


def main() -> None:
    stdscr = curses.initscr()

    curses.noecho()
    curses.nonl()
    curses.start_color()

    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_RED)

    words = get_char_arr()
    cur = 0

    printer(cur, words, stdscr)

    while True:
        key = stdscr.getkey()

        # TODO: C-w | C-backspace removes one word
        if key == "\x1b":
            cur = 0
            words = get_char_arr()
            printer(cur, words, stdscr)
            continue
        if key == "\x7f":
            if not cur > 0:
                continue
            cur -= 1
            words[cur].typed = words[cur].char
            words[cur].state = CharState.DEFAULT
            printer(cur, words, stdscr)
            continue
        if key == "KEY_RESIZE":
            stdscr.clear()
            printer(cur, words, stdscr)
            continue
        if cur == len(words) or key == "\r":
            continue

        # key = convert_char(key, COLEMAK, QWERTY)
        if key == words[cur].char:
            words[cur].state = CharState.CORRECT
        else:
            words[cur].typed = key
            words[cur].state = CharState.INCORRECT

        cur += 1

        printer(cur, words, stdscr)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        curses.endwin()
        exit(0)
