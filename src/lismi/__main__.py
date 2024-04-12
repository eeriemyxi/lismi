import argparse
import curses
import dataclasses
import enum
import importlib.metadata
import io
import math
import pathlib
import random
import time
import typing

COLEMAK = list("qqwwffppggjjlluuyy;:[{]}aarrssttddhhnneeiioo'\"zzxxccvvbbkkmm,<.>/?")
QWERTY = list("qqwweerrttyyuuiioopp[{]}aassddffgghhjjkkll;:'\"zzxxccvvbbnnmm,<.>/?")
SCRIPT_DIR = pathlib.Path(__file__).parent
MAX_SPACES = 10
"""Minimum: 2"""
WORD_COUNT = 20
SKIP_WORDS = False
QUICK_END = False
TARGET_LAYOUT = "qwerty"
EMULATE_LAYOUT = "qwerty"

parser = argparse.ArgumentParser(
    description="Lismi - A simple typing frontend for terminals."
)
parser.add_argument(
    "-w",
    "--word-count",
    type=int,
    default=WORD_COUNT,
    help=f"Number of words per test. Default: {WORD_COUNT!r}.",
)
parser.add_argument(
    "-s",
    "--skip-words",
    action="store_true",
    default=SKIP_WORDS,
    help="Space skips words.",
)
parser.add_argument(
    "-t",
    "--target-layout",
    default=TARGET_LAYOUT,
    help=f"Target layout. Default: {TARGET_LAYOUT!r}. Available: qwerty, colemak.",
)
parser.add_argument(
    "-e",
    "--emulate-layout",
    default=EMULATE_LAYOUT,
    help=f"Emulate layout. Default: {EMULATE_LAYOUT!r}. Available: qwerty, colemak.",
)
parser.add_argument(
    "-m",
    "--max-spaces",
    default=MAX_SPACES,
    type=int,
    help=f"Max spaces per line. Default: {MAX_SPACES!r}. Minimum: 2.",
)
parser.add_argument(
    "-q",
    "--quick-end",
    default=QUICK_END,
    action="store_true",
    help=f"Quickly end test by ignoring last space. Default: {QUICK_END!r}.",
)
parser.add_argument(
    "-V",
    "--version",
    action="version",
    version=importlib.metadata.version("lismi"),
    help="Show program version.",
)
cli_args = parser.parse_args()

MAX_SPACES = cli_args.max_spaces if cli_args.max_spaces > 2 else 2
WORD_COUNT = cli_args.word_count
SKIP_WORDS = cli_args.skip_words
QUICK_END = cli_args.quick_end
TARGET_LAYOUT = globals()[cli_args.target_layout.upper()]
EMULATE_LAYOUT = globals()[cli_args.emulate_layout.upper()]


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
    if ei := get_index(target_layout, char):
        return emulate_layout[ei]
    return char


def get_words(count: int) -> str:
    with open(SCRIPT_DIR / "words" / "two-hundred.txt") as file:
        return " ".join(random.choices(file.read().split(), k=count))  # noqa:S311


def lrgst_k_sp_ss(k: int, arr: list[Char]) -> tuple[str, int]:
    """Find largest k-space-separated substring."""
    s = io.StringIO()
    cc = 0
    lrg = ""
    sx = 0

    for c in arr:
        s.write(c.char)
        if c.char == " ":
            if cc == k:
                sx += 1
                cc = 0
                if len(_s := s.getvalue()) > len(lrg):
                    lrg = _s
                s.seek(0)
                s.truncate(0)
            else:
                cc += 1
    if not lrg:
        lrg = s.getvalue()

    return lrg, sx


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
def _calc_ss(x: int, ss: int, chars: list[Char], max_w: int) -> tuple[int, int, int]:
    sx = 0
    while (x - ((math.floor(x / 2) - math.floor(ss / 2)) + ss)) < 3:
        max_w -= 1
        if max_w <= 2:
            max_w = 2
            break
        _ss, sx = lrgst_k_sp_ss(max_w - 1, chars)
        ss = len(_ss)
    return max_w, ss, sx


def report_printer(stdscr: curses.window, cc: int, ic: int, minutes: float) -> None:
    stdscr.clear()
    curses.curs_set(0)
    y, x = stdscr.getmaxyx()
    outp = []
    gwpm = math.ceil((cc / 5) / minutes)
    nwpm = math.ceil(((cc - ic) / 5) / minutes)
    try:
        accuracy = math.ceil(nwpm / gwpm * 100)
    except ZeroDivisionError:
        accuracy = 0
    outp.append(f"Gross WPM: {gwpm if gwpm > 0 else 0}")
    outp.append(f"Net WPM: {nwpm if nwpm > 0 else 0}")
    outp.append(f"Accuracy: {accuracy if accuracy > 0 else 0}%")
    lrg = max(map(len, outp))
    for i in range(len(outp)):
        stdscr.addstr((y // 2 - len(outp) // 2) + i, x // 2 - lrg // 2, outp[i] + "\n")


def printer(chars: list[Char], stdscr: curses.window, max_w: int, ss: int) -> None:
    # FIXME: errors when text is out of bound
    stdscr.clear()

    y, x = stdscr.getmaxyx()
    max_w, ss, sx = _calc_ss(x, ss, chars, max_w)

    ax = math.floor(x / 2) - math.floor(ss / 2)
    ax = ax if ax > 0 else 0
    ay = math.floor(y / 2) - math.floor(sx / 2)
    ay = ay if ay > 0 else 0

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


def next_space_index(chars: list[Char], cur: int) -> int | None:
    for i, c in enumerate(chars[cur:]):
        if c.char == " ":
            return cur + i
    return None


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
    ss, _ = lrgst_k_sp_ss(MAX_SPACES, chars)
    ss = len(ss)
    cur = 0
    start_time = time.time()
    _report_printed = False

    p_args = (chars, stdscr, MAX_SPACES, ss)
    printer(*p_args)

    while True:
        if cur >= len(chars) - QUICK_END and not _report_printed:
            cc = 0
            ic = 0
            end_time = time.time()
            minutes = (end_time - start_time) / 60
            for c in chars:
                if c.state == CharState.CORRECT:
                    cc += 1
                if c.state == CharState.INCORRECT:
                    ic += 1
            report_printer(stdscr, cc, ic, minutes)
            _report_printed = True
            continue

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
            _cache.cache_ = {}  # type: ignore
            chars = get_char_arr()
            ss, _ = lrgst_k_sp_ss(MAX_SPACES, chars)
            ss = len(ss)
            cur = 0
            start_time = time.time()
            _report_printed = False
            curses.curs_set(1)
            p_args = (chars, stdscr, MAX_SPACES, ss)
            printer(*p_args)
            continue
        if key == "\x7f":  # backspace
            if not cur > 0:
                continue
            rem_char(chars, cur - 1)
            cur -= 1
            _report_printed = False
            curses.curs_set(1)
            printer(*p_args)
            continue
        if cur == len(chars) - QUICK_END:
            continue
        if key == "\r" or key == "KEY_RESIZE":
            printer(*p_args)
            continue
        if SKIP_WORDS and key == " " and cur < len(chars) and chars[cur].char != " ":
            np = next_space_index(chars, cur)
            for c in chars[cur : np + 1]:
                c.state = CharState.INCORRECT
            cur = np + 1
            printer(*p_args)
            continue

        key = convert_char(key, TARGET_LAYOUT, EMULATE_LAYOUT)

        if len(chars) <= cur:
            continue

        if key == chars[cur].char:
            chars[cur].state = CharState.CORRECT
        else:
            chars[cur].typed = key
            chars[cur].state = CharState.INCORRECT

        cur += 1

        printer(*p_args)


def _main() -> None:
    try:
        main()
    except KeyboardInterrupt:
        curses.endwin()
        exit(0)
    except Exception as err:
        curses.endwin()
        raise err


if __name__ == "__main__":
    _main()
