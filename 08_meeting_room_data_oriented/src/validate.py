"""検証。スキーマで言える形の検査と、スキーマでは言えない関係の検査を分けて持つ

どの関数も、問題の説明（文字列）のリストを返す。空リストなら問題なし。
"""

from jsonschema import Draft202012Validator
from schemas import BOOKING, ROOM, SCHEDULE, SLOT, USER
from slots import overlaps


def _shape_errors(schema: dict, data) -> list[str]:
    return [
        f"{'/'.join(str(p) for p in e.absolute_path) or '(root)'}: {e.message}"
        for e in Draft202012Validator(schema).iter_errors(data)
    ]


def user_errors(user) -> list[str]:
    return _shape_errors(USER, user)


def room_errors(room) -> list[str]:
    return _shape_errors(ROOM, room)


def booking_errors(booking) -> list[str]:
    return _shape_errors(BOOKING, booking)


def slot_errors(slot) -> list[str]:
    errors = _shape_errors(SLOT, slot)
    if errors:
        return errors
    # start < end は複数の項目にまたがるので、スキーマでは言えない
    return [] if slot["start"] < slot["end"] else ["start < end でない"]


def schedule_errors(schedule) -> list[str]:
    errors = _shape_errors(SCHEDULE, schedule)
    if errors:
        return errors
    slots = [b["slot"] for b in schedule["bookings"]]
    errors = [f"bookings/{i}/slot: {e}" for i, s in enumerate(slots) for e in slot_errors(s)]
    # 予約同士が重ならない、も複数の要素にまたがるのでスキーマでは言えない
    errors += [
        f"bookings/{i} と bookings/{j} が重なる"
        for i, a in enumerate(slots)
        for j, b in enumerate(slots)
        if i < j and overlaps(a, b)
    ]
    return errors
