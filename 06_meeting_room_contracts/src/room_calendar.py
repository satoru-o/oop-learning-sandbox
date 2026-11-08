from reservation import Reservation
from room import Room
from time_slot import TimeSlot
from user import User


class RoomCalendar:
    def __init__(self, room: Room):
        self.room = room
        self.reservations = []

        self._check_invariant()

    def reserve(self, user: User, slot: TimeSlot):
        self._check_invariant()

        if not self.room.can_use(user):
            raise AssertionError("事前条件違反(その人は会議室を使えない)")
        if not self.is_available(slot):
            raise AssertionError("事前条件違反(空いていない時間帯に予約不可能)")
        before = len(self.reservations)

        reservation = Reservation(user, slot)
        self.reservations.append(reservation)

        if len(self.reservations) != before + 1:
            raise AssertionError("事後条件違反(予約が1件増えていない)")

        self._check_invariant()

        return reservation

    def cancel(self, reservation):
        self._check_invariant()

        if reservation not in self.reservations:
            raise AssertionError("事前条件違反(存在しない予約は取り消せない)")
        before = len(self.reservations)

        self.reservations.remove(reservation)

        if len(self.reservations) != before - 1:
            raise AssertionError("事後条件違反(予約が1件減っていない)")

        self._check_invariant()

    def is_available(self, slot: TimeSlot) -> bool:
        for reservation in self.reservations:
            if reservation.slot.overlaps(slot):
                return False
        return True

    def _check_invariant(self):
        for i, a in enumerate(self.reservations):
            for b in self.reservations[i + 1:]:
                if a.slot.overlaps(b.slot):
                    raise AssertionError("不変条件違反(予約同士が重なっている)")
