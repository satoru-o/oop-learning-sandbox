from datetime import date

import pytest
from models import REGULAR, STUDENT, Book, Loan, Member


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
