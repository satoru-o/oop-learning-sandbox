"""予約のロジック。データを受け取ってデータを返す関数だけで、元のデータは書き換えない

失敗も例外ではなくデータで返す:
  {"ok": True, "schedule": ..., "booking": ...} / {"ok": False, "error": "overlapped"}
"""

from rooms import can_use
from slots import overlaps
from validate import slot_errors, user_errors


def new_schedule(room: dict) -> dict:
    return {"room": room, "bookings": []}


def is_available(schedule: dict, slot: dict) -> bool:
    return all(not overlaps(b["slot"], slot) for b in schedule["bookings"])


def reserve(schedule: dict, user: dict, slot: dict) -> dict:
    if errors := user_errors(user):
        return {"ok": False, "error": "invalid_user", "details": errors}
    if errors := slot_errors(slot):
        return {"ok": False, "error": "invalid_slot", "details": errors}
    if not can_use(schedule["room"], user):
        return {"ok": False, "error": "not_allowed"}
    if not is_available(schedule, slot):
        return {"ok": False, "error": "overlapped"}
    booking = {"user": user, "slot": slot}
    new = {**schedule, "bookings": [*schedule["bookings"], booking]}
    return {"ok": True, "schedule": new, "booking": booking}


def cancel(schedule: dict, booking: dict) -> dict:
    if booking not in schedule["bookings"]:
        return {"ok": False, "error": "not_found"}
    rest = [b for b in schedule["bookings"] if b != booking]
    return {"ok": True, "schedule": {**schedule, "bookings": rest}}
