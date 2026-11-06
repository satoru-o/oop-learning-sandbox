from reservation import Reservation
from room import Room
from time_slot import TimeSlot


class RoomCalendar:
    def __init__(self, room: Room):
        self.room = room
        self.reservations = []

    def reserve(self, user, slot):
        if not self.is_available(slot):
            raise AssertionError("事前条件違反(空いていない時間帯に予約不可能)")
        before = len(self.reservations)

        reservation = Reservation(user, slot)
        self.reservations.append(reservation)

        if len(self.reservations) != before + 1:
            raise AssertionError("事後条件違反(予約が1件増えていない)")
        return reservation

    def is_available(self, slot: TimeSlot) -> bool:
        for reservation in self.reservations:
            if reservation.slot.overlaps(slot):
                return False
        return True
