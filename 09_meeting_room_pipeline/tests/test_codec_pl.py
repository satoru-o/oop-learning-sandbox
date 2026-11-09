from datetime import datetime

import pytest
from codec import schedule_from_dict, schedule_to_dict
from domain import Booking, Position, Room, Schedule, Slot, User

room = Room("役員室", Position.EXECUTIVE)
booking = Booking(
    User("神田", Position.EXECUTIVE),
    Slot(datetime(2026, 11, 3, 10, 0), datetime(2026, 11, 3, 11, 0)),
)


def test_辞書にして戻すと元のスケジュールになる():
    schedule = Schedule(room, (booking,))
    assert schedule_from_dict(schedule_to_dict(schedule)) == schedule


def test_項目が足りないデータはValueErrorになる():
    with pytest.raises(ValueError):
        schedule_from_dict({"room": {"name": "会議室A"}, "bookings": []})


def test_知らない役職はValueErrorになる():
    data = schedule_to_dict(Schedule(room, (booking,)))
    data["bookings"][0]["user"]["position"] = "BOSS"
    with pytest.raises(ValueError):
        schedule_from_dict(data)


def test_不変条件を破るデータはValueErrorになる():
    data = schedule_to_dict(Schedule(room, (booking,)))
    data["bookings"][0]["slot"]["end"] = data["bookings"][0]["slot"]["start"]
    with pytest.raises(ValueError):
        schedule_from_dict(data)
