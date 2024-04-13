import argparse
import curses
import importlib.metadata
import pathlib

from src.lismi import struct, typer, util

COLEMAK = list("qqwwffppggjjlluuyy;:[{]}aarrssttddhhnneeiioo'\"zzxxccvvbbkkmm,<.>/?")
QWERTY = list("qqwweerrttyyuuiioopp[{]}aassddffgghhjjkkll;:'\"zzxxccvvbbnnmm,<.>/?")
SCRIPT_DIR = pathlib.Path(__file__).parent
WORD_FILE = SCRIPT_DIR / "words" / "two-hundred.txt"
MAX_SPACES = 10
"""Minimum: 2"""
WORD_COUNT = 20
SKIP_WORDS = False
NO_QUICK_END = True
TARGET_LAYOUT = "qwerty"
EMULATE_LAYOUT = "qwerty"
ONE_SHOT = False

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
    "-W",
    "--word-file",
    default=WORD_FILE,
    help=f"Word file. Defaults (currently) to {str(WORD_FILE)!r}.",
)
parser.add_argument(
    "-p",
    "--prepend-script-directory",
    action="store_true",
    help="Look for the word file in the script directory's dedicated folder.",
)
parser.add_argument(
    "-s",
    "--skip-words",
    action="store_true",
    default=SKIP_WORDS,
    help="Space skips words.",
)
parser.add_argument(
    "-S",
    "--one-shot",
    action="store_true",
    default=ONE_SHOT,
    help="Exit after first test.",
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
    "--no-quick-end",
    default=NO_QUICK_END,
    action="store_false",
    help="Disable quickly ending test by ignoring last space. "
    f"Default: {NO_QUICK_END!r}.",
)
parser.add_argument(
    "-V",
    "--version",
    action="version",
    version=importlib.metadata.version("lismi"),
    help="Show program version.",
)
cli_args = parser.parse_args()

WORD_FILE = cli_args.word_file
if cli_args.prepend_script_directory:
    WORD_FILE = SCRIPT_DIR / "words" / WORD_FILE

MAX_SPACES = cli_args.max_spaces if cli_args.max_spaces > 2 else 2
WORD_COUNT = cli_args.word_count
SKIP_WORDS = cli_args.skip_words
NO_QUICK_END = cli_args.no_quick_end
ONE_SHOT = cli_args.one_shot
TARGET_LAYOUT = globals()[cli_args.target_layout.upper()]
EMULATE_LAYOUT = globals()[cli_args.emulate_layout.upper()]


STATE_COLORS = {
    struct.CharState.CORRECT: 1,
    struct.CharState.INCORRECT: 2,
    struct.CharState.DEFAULT: 3,
}


def main() -> None:
    stdscr = curses.initscr()

    curses.noecho()
    curses.nonl()
    curses.start_color()

    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_RED)

    start_again = True
    while start_again:
        chars = util.get_char_arr(WORD_FILE, WORD_COUNT)
        curses.curs_set(1)
        start_again = typer.typer(
            stdscr,
            chars,
            STATE_COLORS,
            MAX_SPACES,
            NO_QUICK_END,
            ONE_SHOT,
            SKIP_WORDS,
            TARGET_LAYOUT,
            EMULATE_LAYOUT,
        )


def _main() -> None:
    try:
        main()
    except KeyboardInterrupt:
        curses.endwin()
        exit(0)
    except Exception as err:
        curses.endwin()
        raise err

    curses.endwin()
    exit(0)


if __name__ == "__main__":
    _main()

# TODO: add live wpm counter
