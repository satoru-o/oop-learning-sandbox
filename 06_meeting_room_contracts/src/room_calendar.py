from reservation import Reservation
from room import Room
from time_slot import TimeSlot


class RoomCalendar:
    def __init__(self, room: Room):
        self.room = room
        self.reservations = []

    def reserve(self, user, slot):
        reservation = Reservation(user, slot)
        self.reservations.append(reservation)
        return reservation

    def is_available(self, slot: TimeSlot) -> bool:
        for reservation in self.reservations:
            if reservation.slot.overlaps(slot):
                return False
        return True
