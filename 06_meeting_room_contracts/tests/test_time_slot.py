from datetime import datetime

import pytest
from time_slot import TimeSlot


def test_重なる枠はoverlapsがTrue():
    a = TimeSlot(datetime(2026, 11, 3, 10, 0), datetime(2026, 11, 3, 11, 0))
    b = TimeSlot(datetime(2026, 11, 3, 10, 30), datetime(2026, 11, 3, 11, 30))
    assert a.overlaps(b)


def test_開始が終了以降だと契約違反():
    with pytest.raises(AssertionError):
        TimeSlot(datetime(2026, 11, 3, 11, 0), datetime(2026, 11, 3, 10, 0))


def test_重ならない枠はoverlapsがFalse():
    a = TimeSlot(datetime(2026, 11, 3, 9, 0), datetime(2026, 11, 3, 10, 0))
    b = TimeSlot(datetime(2026, 11, 3, 10, 30), datetime(2026, 11, 3, 11, 30))
    assert not a.overlaps(b)


def test_隣り合う枠はoverlapsがFalse():
    a = TimeSlot(datetime(2026, 11, 3, 10, 0), datetime(2026, 11, 3, 11, 0))
    b = TimeSlot(datetime(2026, 11, 3, 11, 0), datetime(2026, 11, 3, 11, 30))
    assert not a.overlaps(b)


def test_overlapsの対称性を満たすこと():
    a = TimeSlot(datetime(2026, 11, 3, 10, 0), datetime(2026, 11, 3, 11, 0))
    b = TimeSlot(datetime(2026, 11, 3, 10, 30), datetime(2026, 11, 3, 11, 30))
    c = TimeSlot(datetime(2026, 10, 3, 10, 0), datetime(2026, 10, 3, 12, 0))
    d = TimeSlot(datetime(2026, 11, 3, 10, 30), datetime(2026, 11, 3, 11, 30))
    assert a.overlaps(b) == b.overlaps(a)
    assert c.overlaps(d) == d.overlaps(c)


def test_開始時間が終了時刻と同時だと契約違反():
    with pytest.raises(AssertionError):
        TimeSlot(datetime(2026, 11, 3, 10, 0), datetime(2026, 11, 3, 10, 0))
