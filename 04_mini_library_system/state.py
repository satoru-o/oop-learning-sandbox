# 04_mini_library_system/state.py
from dataclasses import dataclass

from models import Book, Loan, Member, Reservation


# LibraryState (図書館全体のスナップショット / イミュータブル)
@dataclass(frozen=True)
class LibraryState:
    """保存・読み込みの単位。操作のたびに新しい LibraryState を作って差し替える"""

    books: tuple[Book, ...] = ()
    members: tuple[Member, ...] = ()
    loans: tuple[Loan, ...] = ()
    reservations: tuple[Reservation, ...] = ()
