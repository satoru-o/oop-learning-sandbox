"""境界。外から来た JSON 相当のデータをドメインの型に変換する（検証して捨てずに、型にする）"""

from datetime import datetime

from domain import Booking, Position, Room, Schedule, Slot, User


def schedule_to_dict(schedule: Schedule) -> dict:
    return {
        "room": {"name": schedule.room.name, "min_position": schedule.room.min_position.name},
        "bookings": [
            {
                "user": {"name": b.user.name, "position": b.user.position.name},
                "slot": {"start": b.slot.start.isoformat(), "end": b.slot.end.isoformat()},
            }
            for b in schedule.bookings
        ],
    }


def schedule_from_dict(data: dict) -> Schedule:
    """形が合わない・不変条件を破るデータは ValueError。壊れた保存データはバグ扱い"""
    try:
        room = Room(data["room"]["name"], Position[data["room"]["min_position"]])
        bookings = tuple(
            Booking(
                User(b["user"]["name"], Position[b["user"]["position"]]),
                Slot(
                    datetime.fromisoformat(b["slot"]["start"]),
                    datetime.fromisoformat(b["slot"]["end"]),
                ),
            )
            for b in data["bookings"]
        )
        return Schedule(room, bookings)
    except (KeyError, TypeError) as e:
        raise ValueError(f"不正なスケジュールデータ: {e!r}") from e
