from time_slot import TimeSlot
from user import User


class Reservation:
    def __init__(self, user: User, slot: TimeSlot):
        self.user = user
        self.slot = slot
