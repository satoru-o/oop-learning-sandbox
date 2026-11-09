from slots import overlaps


def slot(start, end):
    return {"start": f"2026-11-03T{start}", "end": f"2026-11-03T{end}"}


def test_重なる枠はTrue():
    assert overlaps(slot("10:00", "11:00"), slot("10:30", "11:30"))


def test_隣り合う枠は重ならない():
    assert not overlaps(slot("10:00", "11:00"), slot("11:00", "11:30"))


def test_左右を入れ替えても同じ結果になる():
    a, b = slot("10:00", "11:00"), slot("10:30", "12:00")
    assert overlaps(a, b) == overlaps(b, a)
