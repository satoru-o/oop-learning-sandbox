from datetime import datetime

import pytest
from calendar_repository import InMemoryCalendarRepository
from position import Position
from room import Room
from room_calendar import RoomCalendar
from time_slot import TimeSlot
from user import User


def test_登録した会議室のカレンダーを取り出せる():
    repo = InMemoryCalendarRepository()
    calendar = RoomCalendar(Room("会議室A"))
    repo.add(calendar)
    assert repo.get("会議室A") is calendar


def test_取り出したカレンダーに予約すると次に取り出したときも残っている():
    repo = InMemoryCalendarRepository()
    repo.add(RoomCalendar(Room("会議室A")))
    slot = TimeSlot(datetime(2026, 11, 3, 10, 0), datetime(2026, 11, 3, 11, 0))

    repo.get("会議室A").reserve(User("朝野", Position.STAFF), slot)

    assert not repo.get("会議室A").is_available(slot)


def test_部屋ごとにカレンダーが分かれている():
    repo = InMemoryCalendarRepository()
    repo.add(RoomCalendar(Room("会議室A")))
    repo.add(RoomCalendar(Room("会議室B")))
    slot = TimeSlot(datetime(2026, 11, 3, 10, 0), datetime(2026, 11, 3, 11, 0))

    repo.get("会議室A").reserve(User("朝野", Position.STAFF), slot)

    assert repo.get("会議室B").is_available(slot)


def test_未登録の会議室を取り出すと契約違反になる():
    with pytest.raises(AssertionError):
        InMemoryCalendarRepository().get("会議室A")


def test_同じ名前の会議室を二重に登録すると契約違反になる():
    repo = InMemoryCalendarRepository()
    repo.add(RoomCalendar(Room("会議室A")))
    with pytest.raises(AssertionError):
        repo.add(RoomCalendar(Room("会議室A")))
