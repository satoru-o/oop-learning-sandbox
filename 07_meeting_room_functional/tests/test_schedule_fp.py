from datetime import datetime

import pytest
from booking import Booking
from people import Position, User
from result import Err, Ok
from schedule import NotAllowed, NotFound, Overlapped, Schedule, cancel, is_available, reserve
from slot import Slot
from venue import MinPosition, Room

staff = User("朝野", Position.STAFF)
executive = User("神田", Position.EXECUTIVE)
room = Room("会議室A")
exec_room = Room("役員室", MinPosition(Position.EXECUTIVE))


def slot(h1, m1, h2, m2):
    return Slot(datetime(2026, 11, 3, h1, m1), datetime(2026, 11, 3, h2, m2))


def test_作ったばかりのスケジュールは予約が空である():
    assert Schedule(room).bookings == ()


def test_予約がなければどの時間帯も空いている():
    assert is_available(Schedule(room), slot(10, 0, 11, 0))


def test_空いている時間帯を予約すると予約が1件増えた新しいスケジュールが返る():
    before = Schedule(room)
    match reserve(before, staff, slot(10, 0, 11, 0)):
        case Ok((after, booking)):
            assert after.bookings == (booking,)
        case other:
            raise AssertionError(other)
    assert before.bookings == ()  # 元は変わらない


def test_重なる時間帯はOverlappedになる():
    s, _ = reserve(Schedule(room), staff, slot(10, 0, 11, 0)).value
    assert reserve(s, executive, slot(10, 30, 11, 30)) == Err(Overlapped())


def test_隣り合う時間帯は予約できる():
    s, _ = reserve(Schedule(room), staff, slot(10, 0, 11, 0)).value
    assert isinstance(reserve(s, staff, slot(11, 0, 11, 30)), Ok)


def test_役員は役員室を予約できる():
    assert isinstance(reserve(Schedule(exec_room), executive, slot(10, 0, 11, 0)), Ok)


def test_一般社員は役員室を予約できずNotAllowedになる():
    assert reserve(Schedule(exec_room), staff, slot(10, 0, 11, 0)) == Err(NotAllowed())


def test_キャンセルすると予約が1件減り枠がまた空く():
    s, booking = reserve(Schedule(room), staff, slot(10, 0, 11, 0)).value
    after = cancel(s, booking).value
    assert after.bookings == ()
    assert is_available(after, slot(10, 0, 11, 0))
    assert s.bookings == (booking,)  # 元は変わらない


def test_存在しない予約のキャンセルはNotFoundになる():
    ghost = Booking(staff, slot(10, 0, 11, 0))
    assert cancel(Schedule(room), ghost) == Err(NotFound())


def test_直接作っても予約同士が重なるScheduleは作れない():
    a = Booking(staff, slot(10, 0, 11, 0))
    b = Booking(executive, slot(10, 30, 11, 30))
    with pytest.raises(ValueError):
        Schedule(room, (a, b))


def test_直接作っても隣り合う予約ならScheduleを作れる():
    a = Booking(staff, slot(10, 0, 11, 0))
    b = Booking(executive, slot(11, 0, 11, 30))
    assert Schedule(room, (a, b)).bookings == (a, b)
