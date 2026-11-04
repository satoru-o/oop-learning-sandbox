from user import User


class Room:
    def __init__(self, name):
        if not name:
            raise AssertionError("不変条件違反(会議室は名前を持つこと)")
        self.name = name

    def can_use(self, user: User):
        return True
