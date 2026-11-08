import icontract
from reservation import Reservation
from room import Room
from time_slot import TimeSlot
from user import User


def _no_overlap(self) -> bool:
    return all(
        not a.slot.overlaps(b.slot)
        for i, a in enumerate(self.reservations)
        for b in self.reservations[i + 1 :]
    )


@icontract.invariant(_no_overlap, "予約同士の時間帯が重ならない")
class RoomCalendar:
    def __init__(self, room: Room):
        self.room = room
        self.reservations = []

    @icontract.require(lambda self, user: self.room.can_use(user), "その人は会議室を使える")
    @icontract.require(lambda self, slot: self.is_available(slot), "空いている時間帯である")
    @icontract.snapshot(lambda self: len(self.reservations), name="count")
    @icontract.ensure(
        lambda self, OLD: len(self.reservations) == OLD.count + 1, "予約が1件増える"
    )
    @icontract.ensure(
        lambda self, result: result in self.reservations, "返した予約が登録されている"
    )
    def reserve(self, user: User, slot: TimeSlot) -> Reservation:
        reservation = Reservation(user, slot)
        self.reservations.append(reservation)
        return reservation

    @icontract.require(
        lambda self, reservation: reservation in self.reservations, "その予約が存在する"
    )
    @icontract.snapshot(lambda self: len(self.reservations), name="count")
    @icontract.ensure(
        lambda self, OLD: len(self.reservations) == OLD.count - 1, "予約が1件減る"
    )
    def cancel(self, reservation: Reservation) -> None:
        self.reservations.remove(reservation)

    def is_available(self, slot: TimeSlot) -> bool:
        return all(not r.slot.overlaps(slot) for r in self.reservations)
