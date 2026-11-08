from datetime import datetime

import pytest
from executive_room import ExecutiveRoom
from position import Position
from room import Room
from room_calendar import RoomCalendar
from time_slot import TimeSlot
from user import User

slot = TimeSlot(datetime(2026, 11, 3, 10, 0), datetime(2026, 11, 3, 11, 0))
staff = User("朝野", Position.STAFF)
executive = User("神田", Position.EXECUTIVE)


def test_役員用会議室は役員が使える():
    assert ExecutiveRoom("役員会議室").can_use(executive)


def test_役員用会議室は一般社員が使えない():
    assert not ExecutiveRoom("役員会議室").can_use(staff)


def test_役員は役員用会議室を予約できる():
    calendar = RoomCalendar(ExecutiveRoom("役員会議室"))
    reservation = calendar.reserve(executive, slot)
    assert reservation in calendar.reservations


def test_一般社員は役員用会議室を予約できない():
    calendar = RoomCalendar(ExecutiveRoom("役員会議室"))
    with pytest.raises(AssertionError):
        calendar.reserve(staff, slot)


def test_一般社員は一般会議室を予約できる():
    calendar = RoomCalendar(Room("会議室A"))
    reservation = calendar.reserve(staff, slot)
    assert reservation in calendar.reservations
