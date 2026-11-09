from datetime import datetime

from booking import Booking
from people import Position, User
from result import Err, Ok
from schedule import Schedule
from schedule_repository import InMemoryScheduleRepository, RoomNotFound
from slot import Slot
from venue import Room


def test_保存したスケジュールを読み出せる():
    repo = InMemoryScheduleRepository()
    schedule = Schedule(Room("会議室A"))
    repo.save(schedule)
    assert repo.load("会議室A") == Ok(schedule)


def test_保存し直すと置き換わる():
    repo = InMemoryScheduleRepository()
    room = Room("会議室A")
    repo.save(Schedule(room))
    slot = Slot(datetime(2026, 11, 3, 10, 0), datetime(2026, 11, 3, 11, 0))
    updated = Schedule(room, (Booking(User("朝野", Position.STAFF), slot),))
    repo.save(updated)
    assert repo.load("会議室A") == Ok(updated)


def test_未登録の会議室はRoomNotFoundになる():
    assert InMemoryScheduleRepository().load("会議室A") == Err(RoomNotFound())
