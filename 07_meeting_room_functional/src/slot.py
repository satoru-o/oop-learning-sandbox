from dataclasses import dataclass
from datetime import datetime

from result import Err, Ok


@dataclass(frozen=True)
class InvalidSlot:
    """start < end を満たさない"""


@dataclass(frozen=True)
class Slot:
    start: datetime
    end: datetime


def make_slot(start: datetime, end: datetime) -> Ok[Slot] | Err[InvalidSlot]:
    """スマートコンストラクタ。start < end の Slot だけがここから生まれる"""
    if start < end:
        return Ok(Slot(start, end))
    return Err(InvalidSlot())


def overlaps(a: Slot, b: Slot) -> bool:
    """半開区間 [start, end) で重なるか。隣り合う枠は重ならない"""
    return a.start < b.end and b.start < a.end
