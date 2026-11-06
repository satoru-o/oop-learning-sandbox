from datetime import datetime

import pytest
from position import Position
from room import Room
from room_calendar import RoomCalendar
from time_slot import TimeSlot
from user import User

room = Room("会議室A")


def test_作ったばかりのカレンダーは予約が空である():
    calendar = RoomCalendar(room)
    assert calendar.reservations == []


def test_予約がなければどの時間帯も空いている():
    slot = TimeSlot(datetime(2026, 11, 3, 10, 0), datetime(2026, 11, 3, 11, 0))
    calendar = RoomCalendar(room)
    assert calendar.is_available(slot)


def test_空いている時間帯を予約すると予約が1件増える():
    calendar = RoomCalendar(room)
    staff = User("朝野", Position.STAFF)
    slot = TimeSlot(datetime(2026, 11, 3, 10, 0), datetime(2026, 11, 3, 11, 0))

    reservation = calendar.reserve(staff, slot)

    assert len(calendar.reservations) == 1
    assert reservation in calendar.reservations


def test_重なる時間帯は空いていない():
    calendar = RoomCalendar(room)
    staff = User("朝野", Position.STAFF)
    slot = TimeSlot(datetime(2026, 11, 3, 10, 0), datetime(2026, 11, 3, 11, 0))
    calendar.reserve(staff, slot)
    assert not calendar.is_available(
        TimeSlot(datetime(2026, 11, 3, 10, 30), datetime(2026, 11, 3, 11, 0)))


def test_隣り合う時間帯は空いている():
    calendar = RoomCalendar(room)
    staff = User("朝野", Position.STAFF)
    slot = TimeSlot(datetime(2026, 11, 3, 10, 0),
                    datetime(2026, 11, 3, 11, 0))
    calendar.reserve(staff, slot)
    assert calendar.is_available(
        TimeSlot(datetime(2026, 11, 3, 11, 0), datetime(2026, 11, 3, 11, 30)))


def test_空いていない時間帯をreserveしたらAssertionError():
    calendar = RoomCalendar(room)
    staff = User("朝野", Position.STAFF)
    slot = TimeSlot(datetime(2026, 11, 3, 10, 0), datetime(2026, 11, 3, 11, 0))
    calendar.reserve(staff, slot)
    with pytest.raises(AssertionError):
        calendar.reserve(staff, TimeSlot(datetime(2026, 11, 3, 10, 0),
                         datetime(2026, 11, 3, 12, 0)))
