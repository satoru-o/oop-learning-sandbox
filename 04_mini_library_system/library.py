# 04_mini_library_system/library.py
# 状態を持つ「殻」。判定・計算は rules.py の純粋関数に任せ、結果を反映するだけ。
from datetime import date

from errors import BookNotFoundError, BookNotOnLoanError, MemberNotFoundError
from models import Book, Loan, Member
from rules import (
    calc_due_date,
    calc_late_fee,
    check_can_borrow,
    count_active_loans,
    is_book_available,
    total_unpaid_fee,
)


class Library:
    def __init__(self):
        self._books: dict[str, Book] = {}
        self._members: dict[str, Member] = {}
        self._loans: list[Loan] = []

    @property
    def loans(self) -> tuple[Loan, ...]:
        """貸出記録（読み取り専用）"""
        return tuple(self._loans)

    def add_book(self, book: Book) -> None:
        self._books[book.book_id] = book

    def add_member(self, member: Member) -> None:
        self._members[member.member_id] = member

    def borrow(self, member_id: str, book_id: str, today: date) -> Loan:
        member = self._get_member(member_id)
        book = self._get_book(book_id)

        check_can_borrow(
            member.policy,
            active_count=count_active_loans(self._loans, member_id),
            unpaid_fee=total_unpaid_fee(self._loans, member_id),
            available=is_book_available(self._loans, book_id),
        )

        loan = Loan(member, book, borrowed_on=today, due_on=calc_due_date(today, member.policy))
        self._loans.append(loan)
        return loan

    def return_book(self, book_id: str, today: date) -> Loan:
        self._get_book(book_id)
        index, loan = self._find_active_loan(book_id)

        late_fee = calc_late_fee(loan.due_on, today, loan.member.policy)
        closed = loan.closed(today, late_fee)
        self._loans[index] = closed
        return closed

    def pay_fee(self, member_id: str) -> int:
        """未払いの延滞料をすべて支払い、支払った合計額を返す"""
        self._get_member(member_id)
        paid_total = total_unpaid_fee(self._loans, member_id)

        for i, loan in enumerate(self._loans):
            if loan.member.member_id == member_id and loan.has_unpaid_fee():
                self._loans[i] = loan.paid()
        return paid_total

    def _get_member(self, member_id: str) -> Member:
        if member_id not in self._members:
            raise MemberNotFoundError(member_id)
        return self._members[member_id]

    def _get_book(self, book_id: str) -> Book:
        if book_id not in self._books:
            raise BookNotFoundError(book_id)
        return self._books[book_id]

    def _find_active_loan(self, book_id: str) -> tuple[int, Loan]:
        for i, loan in enumerate(self._loans):
            if loan.book.book_id == book_id and loan.is_active():
                return i, loan
        raise BookNotOnLoanError(book_id)
