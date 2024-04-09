import argparse
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
MAX_SPACES = 10
WORD_COUNT = 20
SKIP_WORDS = False
"""Minimum: 2"""

parser = argparse.ArgumentParser()
parser.add_argument(
    "-w", "--word-count", type=int, default=WORD_COUNT, help="Number of words per test."
)
parser.add_argument(
    "-s", "--skip-words", type=bool, default=SKIP_WORDS, help="Space skips words."
)
cli_args = parser.parse_args()

WORD_COUNT = cli_args.word_count
SKIP_WORDS = cli_args.skip_words


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


def get_words(count: int) -> str:
    with open(SCRIPT_DIR / "words" / "two-hundred.txt") as file:
        return " ".join(random.choices(file.read().split(), k=count))  # noqa:S311


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
    return [Char(c, typed=c, state=CharState.DEFAULT) for c in get_words(WORD_COUNT)]


# https://stackoverflow.com/a/66002772/22818367
def _cache(fun: typing.Callable) -> typing.Callable:  # type: ignore
    _cache.cache_ = {}  # type: ignore

    def inner(x: int, *args: list) -> int:  # type: ignore
        if x not in _cache.cache_:  # type: ignore
            _cache.cache_[x] = fun(x, *args)  # type: ignore
        return _cache.cache_[x]  # type: ignore

    return inner


@_cache
def _calc_ss(x: int, ss: int, chars: list[Char], max_w: int) -> tuple[int, int]:
    while (x - ((x // 2 - ss // 2) + ss)) < 10:
        max_w -= 1
        if max_w <= 2:
            max_w = 2
            break
        ss = len(lrgst_k_sp_ss(max_w - 1, chars))
    return max_w, ss


def printer(chars: list[Char], stdscr: curses.window, max_w: int, ss: int) -> None:
    # FIXME: errors when text is out of bound
    stdscr.clear()

    y, x = stdscr.getmaxyx()
    max_w, ss = _calc_ss(x, ss, chars, max_w)

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


def next_space_index(chars: list[Char], cur: int) -> int:
    for i, c in enumerate(chars[cur:]):
        if c.char == " ":
            return cur + i
    return -1


def rem_char(chars: list[Char], cur: int) -> None:
    chars[cur].state = CharState.DEFAULT
    chars[cur].typed = chars[cur].char
    cur -= 1


def main() -> None:  # noqa: C901
    stdscr = curses.initscr()

    curses.noecho()
    curses.nonl()
    curses.start_color()

    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_RED)

    chars = get_char_arr()
    ss = len(lrgst_k_sp_ss(MAX_SPACES, chars))
    cur = 0

    p_args = (chars, stdscr, MAX_SPACES, ss)
    printer(*p_args)

    while True:
        key = stdscr.getkey()

        if key == "\x17" or key == "\x08":  # c-w | c-backspace
            if chars[cur - 1].char == " ":
                rem_char(chars, cur - 1)
                cur -= 1
            while chars[cur - 1].char != " ":
                if cur == 0:
                    break
                rem_char(chars, cur - 1)
                cur -= 1
            p_args = (chars, stdscr, MAX_SPACES, ss)
            printer(*p_args)
            continue
        if key == "\x1b":  # esc
            chars = get_char_arr()
            ss = len(lrgst_k_sp_ss(MAX_SPACES, chars))
            cur = 0
            p_args = (chars, stdscr, MAX_SPACES, ss)
            printer(*p_args)
            continue
        if key == "\x7f":  # backspace
            if not cur > 0:
                continue
            rem_char(chars, cur - 1)
            cur -= 1
            printer(*p_args)
            continue
        if key == "KEY_RESIZE":
            printer(*p_args)
            continue
        if cur == len(chars) or key == "\r":
            continue
        if SKIP_WORDS and key == " " and chars[cur].char != " ":
            np = next_space_index(chars, cur)
            for c in chars[cur : np + 1]:
                c.state = CharState.INCORRECT
            cur = np + 1
            printer(*p_args)
            continue

        # key = convert_char(key, COLEMAK, QWERTY)

        if key == chars[cur].char:
            chars[cur].state = CharState.CORRECT
        else:
            chars[cur].typed = key
            chars[cur].state = CharState.INCORRECT

        cur += 1

        printer(*p_args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        curses.endwin()
        exit(0)