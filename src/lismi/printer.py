import curses
import math

from lismi import struct, util


def report_printer(
    stdscr: curses.window,
    cc: int,
    ic: int,
    minutes: float,
    layout: struct.SupportedLayout,
) -> None:
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
    outp.append(f"Keyboard Layout: {layout.name}")
    lrg = max(map(len, outp))
    for i in range(len(outp)):
        stdscr.addstr((y // 2 - len(outp) // 2) + i, x // 2 - lrg // 2, outp[i] + "\n")


def typer_printer(
    state_colors: dict[struct.CharState, int],
    chars: list[struct.Char],
    stdscr: curses.window,
    max_w: int,
    ss: int,
) -> None:
    # FIXME: errors when text is out of bound
    stdscr.clear()

    y, x = stdscr.getmaxyx()
    max_w, ss, sx = util._calc_ideal_ss(x, ss, chars, max_w)

    ax = math.floor(x / 2) - math.floor(ss / 2)
    ax = ax if ax > 0 else 0
    ay = math.floor(y / 2) - math.floor(sx / 2)
    ay = ay if ay > 0 else 0

    cx, cy = 0, 0
    cc = ccc = 0
    pl = 0

    stdscr.move(ay, ax)

    for c in chars:
        col = state_colors[c.state]

        if c.state is struct.CharState.INCORRECT and c.typed == " ":
            col = 4

        stdscr.addch(c.typed, curses.color_pair(col))

        if c.state != struct.CharState.DEFAULT:
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
