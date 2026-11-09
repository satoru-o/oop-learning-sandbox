from datetime import datetime

import pytest
from domain import (
    Booking,
    Error,
    InvariantViolation,
    Position,
    Room,
    Schedule,
    Slot,
    User,
    has_overlap,
    is_available,
    make_schedule,
    overlaps,
)

staff = User("朝野", Position.STAFF)
room = Room("会議室A")


def slot(start, end):
    return Slot(datetime(2026, 11, 3, *start), datetime(2026, 11, 3, *end))


def test_startがend以上のSlotは作れない():
    with pytest.raises(InvariantViolation):
        slot((11, 0), (10, 0))
    with pytest.raises(InvariantViolation):
        slot((10, 0), (10, 0))


def test_名前が空のUserとRoomは作れない():
    with pytest.raises(InvariantViolation):
        User("", Position.STAFF)
    with pytest.raises(InvariantViolation):
        Room("")


def test_既定の会議室は誰でも使える設定になる():
    assert Room("会議室A").min_position == Position.STAFF


def test_重なる枠はoverlapsがTrueで隣り合う枠はFalse():
    assert overlaps(slot((10, 0), (11, 0)), slot((10, 30), (11, 30)))
    assert not overlaps(slot((10, 0), (11, 0)), slot((11, 0), (11, 30)))


def test_重なる予約を持つScheduleは直接作れない():
    a = Booking(staff, slot((10, 0), (11, 0)))
    b = Booking(staff, slot((10, 30), (11, 30)))
    with pytest.raises(InvariantViolation):
        Schedule(room, (a, b))


def test_make_scheduleは重なると例外ではなくErrorを返す():
    a = Booking(staff, slot((10, 0), (11, 0)))
    b = Booking(staff, slot((10, 30), (11, 30)))
    assert make_schedule(room, (a, b)) == Error.OVERLAPPED


def test_make_scheduleは重ならなければScheduleを返す():
    a = Booking(staff, slot((10, 0), (11, 0)))
    b = Booking(staff, slot((11, 0), (11, 30)))
    assert make_schedule(room, (a, b)) == Schedule(room, (a, b))
    assert not has_overlap((a, b))


def test_is_availableは予約と重なるかどうかで決まる():
    s = Schedule(room, (Booking(staff, slot((10, 0), (11, 0))),))
    assert not is_available(s, slot((10, 30), (11, 30)))
    assert is_available(s, slot((11, 0), (11, 30)))
