"""読む → 純粋関数で決める → 書く、の薄い殻。副作用（リポジトリ）はここにだけ置く"""

from booking import Booking
from people import User
from result import Err, Ok
from schedule import NotAllowed, NotFound, Overlapped, cancel, reserve
from schedule_repository import RoomNotFound, ScheduleRepository
from slot import Slot


def reserve_room(
    repo: ScheduleRepository, room_name: str, user: User, slot: Slot
) -> Ok[Booking] | Err[RoomNotFound | NotAllowed | Overlapped]:
    match repo.load(room_name):
        case Err() as e:
            return e
        case Ok(schedule):
            pass
    match reserve(schedule, user, slot):
        case Err() as e:
            return e
        case Ok((new_schedule, booking)):
            repo.save(new_schedule)
            return Ok(booking)


def cancel_booking(
    repo: ScheduleRepository, room_name: str, booking: Booking
) -> Ok[None] | Err[RoomNotFound | NotFound]:
    match repo.load(room_name):
        case Err() as e:
            return e
        case Ok(schedule):
            pass
    match cancel(schedule, booking):
        case Err() as e:
            return e
        case Ok(new_schedule):
            repo.save(new_schedule)
            return Ok(None)
