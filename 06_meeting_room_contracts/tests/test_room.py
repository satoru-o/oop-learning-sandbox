import pytest
from position import Position
from room import Room
from user import User


def test_会議室は名前を必ず持つ():
    with pytest.raises(AssertionError):
        Room("")

    with pytest.raises(AssertionError):
        Room(None)


def test_一般会議室は役職に関わらず使用可能():
    room = Room("会議室A")
    staff = User("朝野", Position.STAFF)
    executive = User("神田", Position.EXECUTIVE)
    assert room.can_use(staff)
    assert room.can_use(executive)
