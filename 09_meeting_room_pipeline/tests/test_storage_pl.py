from datetime import datetime

from domain import Booking, Error, Position, Room, Schedule, Slot, User
from pipeline import cancel, reserve
from shell import update_room
from storage import InMemoryScheduleRepository

staff = User("朝野", Position.STAFF)
executive = User("神田", Position.EXECUTIVE)
slot = Slot(datetime(2026, 11, 3, 10, 0), datetime(2026, 11, 3, 11, 0))


def make_repo():
    repo = InMemoryScheduleRepository()
    repo.save(Schedule(Room("会議室A")))
    repo.save(Schedule(Room("役員室", Position.EXECUTIVE)))
    return repo


def test_保存したスケジュールを読み出せる():
    repo = InMemoryScheduleRepository()
    schedule = Schedule(Room("会議室A"))
    repo.save(schedule)
    assert repo.load("会議室A") == schedule


def test_未登録の会議室はROOM_NOT_FOUNDになる():
    assert InMemoryScheduleRepository().load("会議室A") == Error.ROOM_NOT_FOUND


def test_予約するとリポジトリに反映される():
    repo = make_repo()
    b = Booking(staff, slot)
    assert update_room(repo, "会議室A", reserve, b) == Schedule(Room("会議室A"), (b,))
    assert repo.load("会議室A") == Schedule(Room("会議室A"), (b,))


def test_失敗したときは保存の内容が変わらない():
    repo = make_repo()
    update_room(repo, "会議室A", reserve, Booking(staff, slot))
    before = repo.load("会議室A")
    assert update_room(repo, "会議室A", reserve, Booking(executive, slot)) == Error.OVERLAPPED
    assert repo.load("会議室A") == before


def test_一般社員は役員室を予約できない():
    assert update_room(make_repo(), "役員室", reserve, Booking(staff, slot)) == Error.NOT_ALLOWED


def test_未登録の会議室への操作はROOM_NOT_FOUNDになる():
    assert (
        update_room(make_repo(), "会議室Z", reserve, Booking(staff, slot)) == Error.ROOM_NOT_FOUND
    )


def test_キャンセルすると保存から予約が消える():
    repo = make_repo()
    b = Booking(staff, slot)
    update_room(repo, "会議室A", reserve, b)
    assert update_room(repo, "会議室A", cancel, b) == Schedule(Room("会議室A"))
    assert repo.load("会議室A") == Schedule(Room("会議室A"))
