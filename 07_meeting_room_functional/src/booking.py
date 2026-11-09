from dataclasses import dataclass

from people import User
from slot import Slot


@dataclass(frozen=True)
class Booking:
    user: User
    slot: Slot
