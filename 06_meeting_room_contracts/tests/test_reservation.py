from datetime import datetime

from position import Position
from reservation import Reservation
from time_slot import TimeSlot
from user import User


def test_予約は予約者と時間帯を持つ():
    staff = User("朝野", Position.STAFF)
    slot = TimeSlot(datetime(2026, 11, 3, 10, 0), datetime(2026, 11, 3, 11, 0))
    reservation = Reservation(staff, slot)
    assert reservation.user == staff
    assert reservation.slot == slot
