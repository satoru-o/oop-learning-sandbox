from validate import room_errors, schedule_errors, slot_errors, user_errors

ok_slot = {"start": "2026-11-03T10:00", "end": "2026-11-03T11:00"}
ok_user = {"name": "朝野", "position": "staff"}
ok_room = {"name": "会議室A", "min_position": "staff"}


def booking(start, end):
    return {"user": ok_user, "slot": {"start": start, "end": end}}


def test_正しい形のデータは問題なし():
    assert user_errors(ok_user) == []
    assert room_errors(ok_room) == []
    assert slot_errors(ok_slot) == []


def test_項目が足りないとスキーマ違反になる():
    assert user_errors({"name": "朝野"})


def test_知らない役職はスキーマ違反になる():
    assert user_errors({"name": "朝野", "position": "boss"})


def test_余計な項目はスキーマ違反になる():
    assert user_errors({**ok_user, "age": 30})


def test_日時の形が違うとスキーマ違反になる():
    assert slot_errors({"start": "11/3 10:00", "end": "2026-11-03T11:00"})


def test_startがend以上の枠は関係の検査で弾く():
    assert slot_errors({"start": "2026-11-03T11:00", "end": "2026-11-03T10:00"})
    assert slot_errors({"start": "2026-11-03T10:00", "end": "2026-11-03T10:00"})


def test_重なる予約を持つスケジュールは問題あり():
    schedule = {
        "room": ok_room,
        "bookings": [
            booking("2026-11-03T10:00", "2026-11-03T11:00"),
            booking("2026-11-03T10:30", "2026-11-03T11:30"),
        ],
    }
    assert schedule_errors(schedule)


def test_隣り合う予約を持つスケジュールは問題なし():
    schedule = {
        "room": ok_room,
        "bookings": [
            booking("2026-11-03T10:00", "2026-11-03T11:00"),
            booking("2026-11-03T11:00", "2026-11-03T11:30"),
        ],
    }
    assert schedule_errors(schedule) == []
