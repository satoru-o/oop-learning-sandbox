import pytest
from schedule_store import InMemoryScheduleStore
from schedules import new_schedule, reserve

room = {"name": "会議室A", "min_position": "staff"}
staff = {"name": "朝野", "position": "staff"}
slot = {"start": "2026-11-03T10:00", "end": "2026-11-03T11:00"}


def test_保存したスケジュールを読み出せる():
    store = InMemoryScheduleStore()
    schedule = new_schedule(room)
    store.save(schedule)
    assert store.load("会議室A") == {"ok": True, "schedule": schedule}


def test_予約を足して保存し直すと置き換わる():
    store = InMemoryScheduleStore()
    store.save(new_schedule(room))
    updated = reserve(new_schedule(room), staff, slot)["schedule"]
    store.save(updated)
    assert store.load("会議室A")["schedule"] == updated


def test_未登録の会議室はroom_not_foundになる():
    assert InMemoryScheduleStore().load("会議室A") == {"ok": False, "error": "room_not_found"}


def test_不正なスケジュールは保存できない():
    with pytest.raises(ValueError):
        InMemoryScheduleStore().save({"room": room})


def test_壊れた保存データは読み込み時に検出する():
    store = InMemoryScheduleStore()
    store._texts["会議室A"] = '{"room": {"name": "会議室A"}, "bookings": []}'
    with pytest.raises(ValueError):
        store.load("会議室A")
