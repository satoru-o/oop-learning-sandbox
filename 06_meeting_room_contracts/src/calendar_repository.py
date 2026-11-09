from typing import Protocol

import icontract
from room_calendar import RoomCalendar


class CalendarRepository(Protocol):
    def get(self, room_name: str) -> RoomCalendar: ...


class InMemoryCalendarRepository:
    """部屋ごとの RoomCalendar を預かる。RoomCalendar は可変なので、同じ実体を返す"""

    def __init__(self):
        self._calendars: dict[str, RoomCalendar] = {}

    @icontract.require(
        lambda self, calendar: calendar.room.name not in self._calendars,
        "同じ名前の会議室を二重に登録しない",
    )
    def add(self, calendar: RoomCalendar) -> None:
        self._calendars[calendar.room.name] = calendar

    @icontract.require(
        lambda self, room_name: room_name in self._calendars, "その会議室が登録されている"
    )
    def get(self, room_name: str) -> RoomCalendar:
        return self._calendars[room_name]
