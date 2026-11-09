from dataclasses import dataclass
from enum import IntEnum


class Position(IntEnum):
    STAFF = 1
    EXECUTIVE = 2


@dataclass(frozen=True)
class User:
    name: str
    position: Position
