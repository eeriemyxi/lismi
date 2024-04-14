import dataclasses
import enum


class CharState(enum.Enum):
    CORRECT = enum.auto()
    INCORRECT = enum.auto()
    DEFAULT = enum.auto()


class SupportedLayout(enum.Enum):
    COLEMAK = tuple(
        "qQwWfFpPgGjJlLuUyY;:[{]}aArRsStTdDhHnNeEiIoO'\"zZxXcCvVbBkKmM,<.>/?"
    )
    QWERTY = tuple(
        "qQwWeErRtTyYuUiIoOpP[{]}aAsSdDfFgGhHjJkKlL;:'\"zZxXcCvVbBnNmM,<.>/?"
    )


@dataclasses.dataclass
class Char:
    char: str
    typed: str
    state: CharState
