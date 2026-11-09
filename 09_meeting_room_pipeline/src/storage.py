"""予約情報の置き場所。クラスを使うのは、差し替えたい所（インターフェース）だけ"""

import json
from typing import Protocol

from codec import schedule_from_dict, schedule_to_dict
from domain import Error, Schedule


class ScheduleRepository(Protocol):
    def load(self, room_name: str) -> Schedule | Error: ...

    def save(self, schedule: Schedule) -> None: ...


class InMemoryScheduleRepository:
    def __init__(self) -> None:
        self._texts: dict[str, str] = {}  # 部屋名 -> JSON 文字列

    def load(self, room_name: str) -> Schedule | Error:
        if room_name not in self._texts:
            return Error.ROOM_NOT_FOUND
        return schedule_from_dict(json.loads(self._texts[room_name]))

    def save(self, schedule: Schedule) -> None:
        self._texts[schedule.room.name] = json.dumps(schedule_to_dict(schedule), ensure_ascii=False)
