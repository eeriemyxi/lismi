import io
import math
import pathlib
import random
import typing

from src.lismi import struct


def get_index(arr: tuple, item: object) -> int | None:
    try:
        return arr.index(item)
    except ValueError:
        return None


def convert_char(
    char: str,
    target_layout: struct.SupportedLayout,
    emulate_layout: struct.SupportedLayout,
) -> str:
    if ei := get_index(target_layout.value, char):
        return emulate_layout.value[ei]
    return char


def get_words(word_file: pathlib.Path, count: int) -> str:
    with open(word_file) as file:
        return " ".join(random.choices(file.read().split(), k=count))  # noqa:S311


def next_space_index(chars: list[struct.Char], cur: int) -> int | None:
    for i, c in enumerate(chars[cur:]):
        if c.char == " ":
            return cur + i
    return None


def rem_char(char: struct.Char) -> None:
    char.state = struct.CharState.DEFAULT
    char.typed = char.char


def get_char_arr(word_file: pathlib.Path, count: int) -> list[struct.Char]:
    return [
        struct.Char(c, typed=c, state=struct.CharState.DEFAULT)
        for c in get_words(word_file, count)
    ] + [struct.Char(" ", " ", struct.CharState.DEFAULT)]


def lrgst_k_sp_ss(k: int, arr: list[struct.Char]) -> tuple[str, int]:
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


# https://stackoverflow.com/a/66002772/22818367
def _ideal_ss_cache(fun: typing.Callable) -> typing.Callable:  # type: ignore
    _ideal_ss_cache.cache_ = {}  # type: ignore

    def inner(x: int, *args: list) -> int:  # type: ignore
        if x not in _ideal_ss_cache.cache_:  # type: ignore
            _ideal_ss_cache.cache_[x] = fun(x, *args)  # type: ignore
        return _ideal_ss_cache.cache_[x]  # type: ignore

    return inner


@_ideal_ss_cache
def _calc_ideal_ss(
    x: int, ss: int, chars: list[struct.Char], max_w: int
) -> tuple[int, int, int]:
    sx = 0
    while (x - ((math.floor(x / 2) - math.floor(ss / 2)) + ss)) < 3:
        max_w -= 1
        if max_w <= 2:
            max_w = 2
            break
        _ss, sx = lrgst_k_sp_ss(max_w - 1, chars)
        ss = len(_ss)
    return max_w, ss, sx
