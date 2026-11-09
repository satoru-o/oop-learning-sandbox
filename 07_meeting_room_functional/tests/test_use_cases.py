from datetime import datetime

from people import Position, User
from result import Err, Ok
from schedule import NotAllowed, NotFound, Overlapped, Schedule
from schedule_repository import InMemoryScheduleRepository, RoomNotFound
from slot import Slot
from use_cases import cancel_booking, reserve_room
from venue import MinPosition, Room

staff = User("朝野", Position.STAFF)
executive = User("神田", Position.EXECUTIVE)
slot = Slot(datetime(2026, 11, 3, 10, 0), datetime(2026, 11, 3, 11, 0))


def make_repo():
    repo = InMemoryScheduleRepository()
    repo.save(Schedule(Room("会議室A")))
    repo.save(Schedule(Room("役員室", MinPosition(Position.EXECUTIVE))))
    return repo


def test_予約するとリポジトリのスケジュールに反映される():
    repo = make_repo()
    booking = reserve_room(repo, "会議室A", staff, slot).value
    assert repo.load("会議室A").value.bookings == (booking,)


def test_埋まっている枠を予約するとOverlappedで保存は変わらない():
    repo = make_repo()
    reserve_room(repo, "会議室A", staff, slot)
    before = repo.load("会議室A")
    assert reserve_room(repo, "会議室A", executive, slot) == Err(Overlapped())
    assert repo.load("会議室A") == before


def test_一般社員は役員室を予約できずNotAllowedになる():
    assert reserve_room(make_repo(), "役員室", staff, slot) == Err(NotAllowed())


def test_未登録の会議室はRoomNotFoundになる():
    assert reserve_room(make_repo(), "会議室Z", staff, slot) == Err(RoomNotFound())


def test_キャンセルするとリポジトリから予約が消えて枠がまた取れる():
    repo = make_repo()
    booking = reserve_room(repo, "会議室A", staff, slot).value
    assert cancel_booking(repo, "会議室A", booking) == Ok(None)
    assert repo.load("会議室A").value.bookings == ()
    assert isinstance(reserve_room(repo, "会議室A", executive, slot), Ok)


def test_存在しない予約のキャンセルはNotFoundになる():
    repo = make_repo()
    booking = reserve_room(repo, "会議室A", staff, slot).value
    cancel_booking(repo, "会議室A", booking)
    assert cancel_booking(repo, "会議室A", booking) == Err(NotFound())
