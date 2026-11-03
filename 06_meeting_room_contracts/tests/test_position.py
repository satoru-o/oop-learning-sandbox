from position import Position


def test_役員は一般社員よりも上():
    assert Position.EXECUTIVE > Position.STAFF


def test_同じ役職は以上を満たす():
    assert Position.EXECUTIVE >= Position.EXECUTIVE
