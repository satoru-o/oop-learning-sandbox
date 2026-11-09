from people import Position, User
from venue import Anyone, MinPosition, Room, can_use

staff = User("朝野", Position.STAFF)
executive = User("神田", Position.EXECUTIVE)


def test_誰でも使える会議室は一般社員も使える():
    assert can_use(Room("会議室A"), staff)


def test_役員室は役員が使える():
    assert can_use(Room("役員室", MinPosition(Position.EXECUTIVE)), executive)


def test_役員室は一般社員が使えない():
    assert not can_use(Room("役員室", MinPosition(Position.EXECUTIVE)), staff)


def test_既定の利用条件はAnyone():
    assert Room("会議室A").access == Anyone()
