from datetime import datetime

import pytest
from result import Err, Ok
from slot import InvalidSlot, Slot, make_slot, overlaps


def at(h, m=0):
    return datetime(2026, 11, 3, h, m)


def test_startがendより前なら作れる():
    assert make_slot(at(10), at(11)) == Ok(Slot(at(10), at(11)))


def test_startがendより後ならErrになる():
    assert make_slot(at(11), at(10)) == Err(InvalidSlot())


def test_startとendが同じ時刻ならErrになる():
    assert make_slot(at(10), at(10)) == Err(InvalidSlot())


def test_重なる枠はoverlapsがTrue():
    assert overlaps(Slot(at(10), at(11)), Slot(at(10, 30), at(11, 30)))


def test_隣り合う枠は重ならない():
    assert not overlaps(Slot(at(10), at(11)), Slot(at(11), at(11, 30)))


def test_overlapsは左右を入れ替えても同じ結果になる():
    a, b = Slot(at(10), at(11)), Slot(at(10, 30), at(12))
    assert overlaps(a, b) == overlaps(b, a)


def test_直接作ってもstartがend以上のSlotは作れない():
    with pytest.raises(ValueError):
        Slot(at(11), at(10))
    with pytest.raises(ValueError):
        Slot(at(10), at(10))
