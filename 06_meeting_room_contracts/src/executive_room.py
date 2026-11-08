from position import Position
from room import Room
from user import User


class ExecutiveRoom(Room):
    def can_use(self, user: User) -> bool:
        return user.position >= Position.EXECUTIVE
