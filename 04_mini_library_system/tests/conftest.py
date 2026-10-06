from datetime import date

import pytest
from models import REGULAR, STUDENT, Book, Loan, Member, Reservation
from state import LibraryState


@pytest.fixture
def regular_member() -> Member:
    return Member("m1", "一般太郎", REGULAR)


@pytest.fixture
def student_member() -> Member:
    return Member("m2", "学生花子", STUDENT)


@pytest.fixture
def book() -> Book:
    return Book("b1", "オブジェクト指向入門")


@pytest.fixture
def borrowed_on() -> date:
    return date(2026, 10, 1)


@pytest.fixture
def active_loan(regular_member, book, borrowed_on) -> Loan:
    """一般会員が借りている最中の Loan（期限は 10/15）"""
    return Loan(regular_member, book, borrowed_on, due_on=date(2026, 10, 15))


@pytest.fixture
def full_state() -> LibraryState:
    """あらゆる種類のデータを含む状態"""
    taro = Member("m1", "一般太郎", REGULAR)
    hanako = Member("m2", "学生花子", STUDENT)
    b1, b2, b3 = Book("b1", "本1"), Book("b2", "本2"), Book("b3", "本3")
    due = date(2026, 10, 15)
    active = Loan(taro, b1, date(2026, 10, 1), due)
    unpaid = Loan(hanako, b2, date(2026, 10, 1), due).closed(date(2026, 10, 20), late_fee=25)
    paid = Loan(hanako, b3, date(2026, 10, 1), due).closed(date(2026, 10, 20), 25).paid()
    return LibraryState(
        books=(b1, b2, b3),
        members=(taro, hanako),
        loans=(active, unpaid, paid),
        reservations=(
            Reservation(hanako, b1, date(2026, 10, 2)),
            Reservation(taro, b2, date(2026, 10, 3), hold_until=date(2026, 10, 27)),
        ),
    )
