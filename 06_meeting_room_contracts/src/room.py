import icontract
from user import User


@icontract.invariant(lambda self: bool(self.name), "会議室は名前を持つこと")
class Room:
    def __init__(self, name):
        self.name = name

    def can_use(self, user: User) -> bool:
        return True
