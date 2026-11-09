"""処理は動詞（reserve / cancel）で切る。ルールの関数を順に通し、全部通ったら適用する

要求が増えたら、ルールの関数を1つ書いてタプルに足すだけ。
"""

from collections.abc import Callable
from dataclasses import replace

from domain import Booking, Error, Schedule, make_schedule

# ルールは「通れば None、だめなら Error」を返す
Rule = Callable[[Schedule, Booking], Error | None]
# 適用は「新しい Schedule、またはError」を返す。元の Schedule は変えない
Apply = Callable[[Schedule, Booking], Schedule | Error]


def check_allowed(schedule: Schedule, booking: Booking) -> Error | None:
    if booking.user.position >= schedule.room.min_position:
        return None
    return Error.NOT_ALLOWED


def check_exists(schedule: Schedule, booking: Booking) -> Error | None:
    return None if booking in schedule.bookings else Error.NOT_FOUND


def add_booking(schedule: Schedule, booking: Booking) -> Schedule | Error:
    # 重なりの検査は make_schedule に任せる（ここに専用のルールは置かない）
    return make_schedule(schedule.room, (*schedule.bookings, booking))


def remove_booking(schedule: Schedule, booking: Booking) -> Schedule:
    return replace(schedule, bookings=tuple(b for b in schedule.bookings if b != booking))


RESERVE_RULES: tuple[Rule, ...] = (check_allowed,)
CANCEL_RULES: tuple[Rule, ...] = (check_exists,)


def run(
    rules: tuple[Rule, ...], apply: Apply, schedule: Schedule, booking: Booking
) -> Schedule | Error:
    for rule in rules:
        if (error := rule(schedule, booking)) is not None:
            return error
    return apply(schedule, booking)


def reserve(schedule: Schedule, booking: Booking) -> Schedule | Error:
    return run(RESERVE_RULES, add_booking, schedule, booking)


def cancel(schedule: Schedule, booking: Booking) -> Schedule | Error:
    return run(CANCEL_RULES, remove_booking, schedule, booking)
