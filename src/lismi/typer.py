import curses
import time

from src.lismi import printer, struct, util


def typer(  # noqa: C901
    stdscr: curses.window,
    chars: list[struct.Char],
    state_colors: dict[struct.CharState, int],
    max_spaces: int,
    no_quick_end: bool,
    one_shot: bool,
    skip_words: bool,
    no_backspace: bool,
    target_layout: struct.SupportedLayout,
    emulate_layout: struct.SupportedLayout,
) -> bool:
    ss, _ = util.lrgst_k_sp_ss(max_spaces, chars)
    ss = len(ss)
    cur = 0
    start_time = time.time()
    _st_reset = False
    _report_printed = False

    p_args = (state_colors, chars, stdscr, max_spaces, ss)
    printer.typer_printer(*p_args)

    while True:
        if cur >= (len(chars) - no_quick_end) and not _report_printed:
            cc = 0
            ic = 0
            end_time = time.time()
            minutes = (end_time - start_time) / 60
            for c in chars:
                if c.state == struct.CharState.CORRECT:
                    cc += 1
                if c.state == struct.CharState.INCORRECT:
                    ic += 1
            printer.report_printer(stdscr, cc, ic, minutes)
            _report_printed = True
            continue

        key = stdscr.getkey()

        if key == "\x17" or key == "\x08":  # c-w | c-backspace
            if no_backspace:
                continue
            if chars[cur - 1].char == " " and cur > 0:
                util.rem_char(chars[cur - 1])
                cur -= 1
            while chars[cur - 1].char != " ":
                if cur == 0:
                    break
                util.rem_char(chars[cur - 1])
                cur -= 1
            p_args = (state_colors, chars, stdscr, max_spaces, ss)
            _report_printed = False
            curses.curs_set(1)
            printer.typer_printer(*p_args)
            continue
        if key == "\x05":  # c-e
            cur = 0
            for c in chars:
                util.rem_char(c)
            _report_printed = False
            _st_reset = False
            curses.curs_set(1)
            printer.typer_printer(*p_args)
            continue
        if key == "\x1b":  # esc
            if one_shot:
                return False
            return True
        if key == "\x7f":  # backspace
            if no_backspace:
                continue
            if not cur > 0:
                continue
            util.rem_char(chars[cur - 1])
            cur -= 1
            _report_printed = False
            curses.curs_set(1)
            printer.typer_printer(*p_args)
            continue
        if cur == len(chars) - no_quick_end:
            continue
        if key == "\r" or key == "KEY_RESIZE":
            printer.typer_printer(*p_args)
            continue
        if skip_words and key == " " and cur < len(chars) and chars[cur].char != " ":
            np = util.next_space_index(chars, cur)
            if not np:
                np = len(chars) - 1
            for c in chars[cur : np + 1]:
                c.state = struct.CharState.INCORRECT
            cur = np + 1
            printer.typer_printer(*p_args)
            continue

        if cur == 0 and not _st_reset:
            _st_reset = True
            start_time = time.time()

        key = util.convert_char(key, target_layout, emulate_layout)

        if len(chars) <= cur:
            continue

        if key == chars[cur].char:
            chars[cur].state = struct.CharState.CORRECT
        else:
            chars[cur].typed = key
            chars[cur].state = struct.CharState.INCORRECT

        cur += 1

        printer.typer_printer(*p_args)
