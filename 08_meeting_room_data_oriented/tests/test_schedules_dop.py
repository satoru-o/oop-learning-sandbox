import copy
import json

from schedules import cancel, is_available, new_schedule, reserve
from validate import schedule_errors

staff = {"name": "朝野", "position": "staff"}
executive = {"name": "神田", "position": "executive"}
room = {"name": "会議室A", "min_position": "staff"}
exec_room = {"name": "役員室", "min_position": "executive"}


def slot(start, end):
    return {"start": f"2026-11-03T{start}", "end": f"2026-11-03T{end}"}


def test_作ったばかりのスケジュールは予約が空である():
    assert new_schedule(room) == {"room": room, "bookings": []}


def test_予約がなければどの時間帯も空いている():
    assert is_available(new_schedule(room), slot("10:00", "11:00"))


def test_空いている時間帯を予約すると予約が1件増えた新しいスケジュールが返る():
    before = new_schedule(room)
    snapshot = copy.deepcopy(before)

    result = reserve(before, staff, slot("10:00", "11:00"))

    assert result["ok"]
    assert result["schedule"]["bookings"] == [result["booking"]]
    assert before == snapshot  # 元のデータは変わらない


def test_重なる時間帯はoverlappedになる():
    s = reserve(new_schedule(room), staff, slot("10:00", "11:00"))["schedule"]
    assert reserve(s, executive, slot("10:30", "11:30")) == {"ok": False, "error": "overlapped"}


def test_隣り合う時間帯は予約できる():
    s = reserve(new_schedule(room), staff, slot("10:00", "11:00"))["schedule"]
    assert reserve(s, staff, slot("11:00", "11:30"))["ok"]


def test_役員は役員室を予約できる():
    assert reserve(new_schedule(exec_room), executive, slot("10:00", "11:00"))["ok"]


def test_一般社員は役員室を予約できずnot_allowedになる():
    result = reserve(new_schedule(exec_room), staff, slot("10:00", "11:00"))
    assert result == {"ok": False, "error": "not_allowed"}


def test_不正な枠はinvalid_slotになる():
    result = reserve(new_schedule(room), staff, slot("11:00", "10:00"))
    assert result["error"] == "invalid_slot"


def test_不正なユーザーはinvalid_userになる():
    result = reserve(
        new_schedule(room), {"name": "朝野", "position": "boss"}, slot("10:00", "11:00")
    )
    assert result["error"] == "invalid_user"


def test_キャンセルすると予約が1件減り枠がまた空く():
    s = reserve(new_schedule(room), staff, slot("10:00", "11:00"))
    snapshot = copy.deepcopy(s["schedule"])

    after = cancel(s["schedule"], s["booking"])

    assert after["schedule"]["bookings"] == []
    assert is_available(after["schedule"], slot("10:00", "11:00"))
    assert s["schedule"] == snapshot  # 元のデータは変わらない


def test_存在しない予約のキャンセルはnot_foundになる():
    ghost = {"user": staff, "slot": slot("10:00", "11:00")}
    assert cancel(new_schedule(room), ghost) == {"ok": False, "error": "not_found"}


def test_予約後のスケジュールはそのままJSONにして戻せて不変条件も満たす():
    s = reserve(new_schedule(room), staff, slot("10:00", "11:00"))["schedule"]
    assert json.loads(json.dumps(s)) == s
    assert schedule_errors(s) == []
