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


def demo() -> None:
    from datetime import timedelta

    from errors import LibraryError
    from models import REGULAR, STUDENT

    today = date(2026, 10, 1)
    library = Library()
    for i in range(1, 6):
        library.add_book(Book(f"b{i}", f"本{i}"))
    library.add_member(Member("m1", "一般太郎", REGULAR))
    library.add_member(Member("m2", "学生花子", STUDENT))

    def attempt(label: str, action) -> None:
        try:
            result = action()
        except LibraryError as e:
            print(f"  ✗ {label}: {e}")
        else:
            print(f"  ✓ {label}: {result}")

    print("【1】一般会員が4冊目を借りようとして、上限エラーになる")
    for book_id in ("b1", "b2", "b3", "b4"):
        attempt(
            f"太郎が {book_id} を借りる", lambda b=book_id: library.borrow("m1", b, today).due_on
        )

    print("【2】貸出中の本を別の会員が借りようとして、エラーになる")
    attempt("花子が b1 を借りる", lambda: library.borrow("m2", "b1", today))

    print("【3】期限を5日過ぎて返却し、延滞料が発生する（一般50円 / 学生25円）")
    library.borrow("m2", "b5", today)
    late = today + timedelta(days=14 + 5)
    attempt("太郎が b1 を返却", lambda: library.return_book("b1", late).late_fee)
    late_student = today + timedelta(days=21 + 5)
    attempt("花子が b5 を返却", lambda: library.return_book("b5", late_student).late_fee)

    print("【4】延滞料を支払うまで、その会員は借りられない")
    attempt("太郎が b4 を借りる", lambda: library.borrow("m1", "b4", late))
    attempt("太郎が延滞料を支払う", lambda: library.pay_fee("m1"))
    attempt("太郎が b4 を借りる", lambda: library.borrow("m1", "b4", late).due_on)


if __name__ == "__main__":
    demo()
