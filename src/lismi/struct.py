import dataclasses
import enum


class CharState(enum.Enum):
    CORRECT = enum.auto()
    INCORRECT = enum.auto()
    DEFAULT = enum.auto()


@dataclasses.dataclass
class Char:
    char: str
    typed: str
    state: CharState
