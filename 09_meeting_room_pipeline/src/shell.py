"""殻。読む → 純粋な処理で決める → 書く。副作用（リポジトリ）はここにだけ置く"""

from collections.abc import Callable

from domain import Booking, Error, Schedule
from storage import ScheduleRepository


def update_room(
    repo: ScheduleRepository,
    room_name: str,
    operation: Callable[[Schedule, Booking], Schedule | Error],
    booking: Booking,
) -> Schedule | Error:
    """operation に reserve / cancel を渡して使う。Error のときは保存しない"""
    loaded = repo.load(room_name)
    if isinstance(loaded, Error):
        return loaded
    updated = operation(loaded, booking)
    if isinstance(updated, Error):
        return updated
    repo.save(updated)
    return updated
