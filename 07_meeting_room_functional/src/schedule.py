from dataclasses import dataclass

from booking import Booking
from people import User
from result import Err, Ok
from slot import Slot, overlaps
from venue import Room, can_use


@dataclass(frozen=True)
class NotAllowed:
    """その人はこの会議室を使えない"""


@dataclass(frozen=True)
class Overlapped:
    """すでに予約のある時間帯と重なる"""


@dataclass(frozen=True)
class NotFound:
    """そんな予約はない"""


@dataclass(frozen=True)
class Schedule:
    room: Room
    bookings: tuple[Booking, ...] = ()


def is_available(schedule: Schedule, slot: Slot) -> bool:
    return all(not overlaps(b.slot, slot) for b in schedule.bookings)


def reserve(
    schedule: Schedule, user: User, slot: Slot
) -> Ok[tuple[Schedule, Booking]] | Err[NotAllowed | Overlapped]:
    """元の Schedule は変えず、予約を足した新しい Schedule と予約を返す"""
    if not can_use(schedule.room, user):
        return Err(NotAllowed())
    if not is_available(schedule, slot):
        return Err(Overlapped())
    booking = Booking(user, slot)
    return Ok((Schedule(schedule.room, (*schedule.bookings, booking)), booking))


def cancel(schedule: Schedule, booking: Booking) -> Ok[Schedule] | Err[NotFound]:
    if booking not in schedule.bookings:
        return Err(NotFound())
    rest = tuple(b for b in schedule.bookings if b != booking)
    return Ok(Schedule(schedule.room, rest))
