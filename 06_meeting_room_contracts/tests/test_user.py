from position import Position
from user import User


def test_Userは名前と役職を持つ():
    a = User("朝野", Position.STAFF)
    assert a.name == "朝野" and a.position == Position.STAFF
