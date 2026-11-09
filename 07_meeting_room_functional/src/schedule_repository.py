from dataclasses import dataclass
from typing import Protocol

from result import Err, Ok
from schedule import Schedule


@dataclass(frozen=True)
class RoomNotFound:
    """その会議室は登録されていない"""


class ScheduleRepository(Protocol):
    def load(self, room_name: str) -> Ok[Schedule] | Err[RoomNotFound]: ...

    def save(self, schedule: Schedule) -> None: ...


class InMemoryScheduleRepository:
    """部屋ごとの Schedule を預かる。Schedule は不変なので、保存は置き換えになる"""

    def __init__(self):
        self._schedules: dict[str, Schedule] = {}

    def load(self, room_name: str) -> Ok[Schedule] | Err[RoomNotFound]:
        if room_name in self._schedules:
            return Ok(self._schedules[room_name])
        return Err(RoomNotFound())

    def save(self, schedule: Schedule) -> None:
        self._schedules[schedule.room.name] = schedule
