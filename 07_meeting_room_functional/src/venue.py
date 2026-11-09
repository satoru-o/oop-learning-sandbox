from dataclasses import dataclass

from people import Position, User


@dataclass(frozen=True)
class Anyone:
    """誰でも使える"""


@dataclass(frozen=True)
class MinPosition:
    """この役職以上だけが使える"""

    position: Position


Access = Anyone | MinPosition


@dataclass(frozen=True)
class Room:
    name: str
    access: Access = Anyone()


def can_use(room: Room, user: User) -> bool:
    # 継承で上書きする代わりに、利用条件をデータにして1つの関数で判定する
    match room.access:
        case Anyone():
            return True
        case MinPosition(position):
            return user.position >= position
