from datetime import datetime

from domain import Booking, Error, Position, Room, Schedule, Slot, User
from pipeline import CANCEL_RULES, RESERVE_RULES, cancel, check_allowed, reserve, run

staff = User("朝野", Position.STAFF)
executive = User("神田", Position.EXECUTIVE)
room = Room("会議室A")
exec_room = Room("役員室", Position.EXECUTIVE)


def booking(user, start, end):
    slot = Slot(datetime(2026, 11, 3, *start), datetime(2026, 11, 3, *end))
    return Booking(user, slot)


def test_空いている時間帯を予約すると予約が1件増えた新しいスケジュールが返る():
    before = Schedule(room)
    b = booking(staff, (10, 0), (11, 0))
    assert reserve(before, b) == Schedule(room, (b,))
    assert before.bookings == ()  # 元は変わらない


def test_重なる時間帯はOVERLAPPEDになる():
    s = reserve(Schedule(room), booking(staff, (10, 0), (11, 0)))
    assert reserve(s, booking(executive, (10, 30), (11, 30))) == Error.OVERLAPPED


def test_隣り合う時間帯は予約できる():
    s = reserve(Schedule(room), booking(staff, (10, 0), (11, 0)))
    assert isinstance(reserve(s, booking(staff, (11, 0), (11, 30))), Schedule)


def test_役員は役員室を予約できる():
    assert isinstance(reserve(Schedule(exec_room), booking(executive, (10, 0), (11, 0))), Schedule)


def test_一般社員は役員室を予約できずNOT_ALLOWEDになる():
    assert reserve(Schedule(exec_room), booking(staff, (10, 0), (11, 0))) == Error.NOT_ALLOWED


def test_キャンセルすると予約が1件減って枠がまた空く():
    b = booking(staff, (10, 0), (11, 0))
    s = reserve(Schedule(room), b)
    assert cancel(s, b) == Schedule(room)
    assert s.bookings == (b,)  # 元は変わらない


def test_存在しない予約のキャンセルはNOT_FOUNDになる():
    assert cancel(Schedule(room), booking(staff, (10, 0), (11, 0))) == Error.NOT_FOUND


def test_ルールの関数をタプルに足すだけで要求を増やせる():
    def no_lunch(schedule, b):
        return Error.NOT_ALLOWED if b.slot.start.hour == 12 else None

    rules = (*RESERVE_RULES, no_lunch)

    def apply(s, b):
        return Schedule(s.room, (*s.bookings, b))

    assert run(rules, apply, Schedule(room), booking(staff, (12, 0), (13, 0))) == Error.NOT_ALLOWED
    assert isinstance(run(rules, apply, Schedule(room), booking(staff, (10, 0), (11, 0))), Schedule)


def test_ルールの一覧が処理の流れとして読める():
    assert RESERVE_RULES == (check_allowed,)
    assert len(CANCEL_RULES) == 1
