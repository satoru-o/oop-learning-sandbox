from rooms import can_use

staff = {"name": "朝野", "position": "staff"}
executive = {"name": "神田", "position": "executive"}
normal = {"name": "会議室A", "min_position": "staff"}
exec_room = {"name": "役員室", "min_position": "executive"}


def test_誰でも使える会議室は一般社員も使える():
    assert can_use(normal, staff)


def test_役員室は役員が使える():
    assert can_use(exec_room, executive)


def test_役員室は一般社員が使えない():
    assert not can_use(exec_room, staff)
