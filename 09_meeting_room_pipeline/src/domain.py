"""データの型と、ただ1つの不変条件。型は名詞（データ）だけで、振る舞いは持たない"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, IntEnum


class Position(IntEnum):
    STAFF = 1
    EXECUTIVE = 2


class Error(Enum):
    """業務上の失敗。普通に起こるので値で返す。バグ（契約違反）は例外で表す"""

    NOT_ALLOWED = "その人はこの会議室を使えない"
    OVERLAPPED = "その時間帯はすでに埋まっている"
    NOT_FOUND = "そんな予約はない"
    ROOM_NOT_FOUND = "その会議室は登録されていない"


class InvariantViolation(ValueError):
    """不変条件を破った値を作ろうとした（呼ぶ側のバグ）"""


@dataclass(frozen=True)
class User:
    name: str
    position: Position

    def __post_init__(self) -> None:
        if not self.name:
            raise InvariantViolation("ユーザーは名前を持つこと")


@dataclass(frozen=True)
class Room:
    name: str
    min_position: Position = Position.STAFF  # STAFF なら誰でも使える。役員室は EXECUTIVE

    def __post_init__(self) -> None:
        if not self.name:
            raise InvariantViolation("会議室は名前を持つこと")


@dataclass(frozen=True)
class Slot:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if not self.start < self.end:
            raise InvariantViolation("start < end")


@dataclass(frozen=True)
class Booking:
    """予約。予約の依頼にも、キャンセルの依頼にも、この型を使う"""

    user: User
    slot: Slot


@dataclass(frozen=True)
class Schedule:
    room: Room
    bookings: tuple[Booking, ...] = ()

    def __post_init__(self) -> None:
        if has_overlap(self.bookings):
            raise InvariantViolation("予約同士の時間帯が重ならない")


def overlaps(a: Slot, b: Slot) -> bool:
    """半開区間 [start, end) で重なるか。隣り合う枠は重ならない"""
    return a.start < b.end and b.start < a.end


def has_overlap(bookings: tuple[Booking, ...]) -> bool:
    """重なりの判定ロジックはここだけ"""
    return any(overlaps(a.slot, b.slot) for i, a in enumerate(bookings) for b in bookings[i + 1 :])


def make_schedule(room: Room, bookings: tuple[Booking, ...]) -> Schedule | Error:
    """業務の流れの中で作るときの入口。重なれば例外ではなく Error を返す"""
    if has_overlap(bookings):
        return Error.OVERLAPPED
    return Schedule(room, bookings)


def is_available(schedule: Schedule, slot: Slot) -> bool:
    return all(not overlaps(b.slot, slot) for b in schedule.bookings)
