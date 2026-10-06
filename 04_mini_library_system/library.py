# 04_mini_library_system/library.py
# 状態を持つ「殻」。判定・計算は rules.py の純粋関数に任せ、結果を反映するだけ。
from datetime import date

from errors import (
    BookNotFoundError,
    BookNotOnLoanError,
    DuplicateBookError,
    DuplicateMemberError,
    MemberNotFoundError,
    ReservationNotFoundError,
)
from models import Book, Loan, Member, Reservation
from rules import (
    calc_due_date,
    calc_late_fee,
    check_can_borrow,
    check_can_reserve,
    count_active_loans,
    is_book_available,
    is_reserved_by_other,
    settle_queue,
    total_unpaid_fee,
)


class Library:
    def __init__(self):
        self._books: dict[str, Book] = {}
        self._members: dict[str, Member] = {}
        self._loans: list[Loan] = []
        self._reservations: list[Reservation] = []

    @property
    def loans(self) -> tuple[Loan, ...]:
        """貸出記録（読み取り専用）"""
        return tuple(self._loans)

    @property
    def reservations(self) -> tuple[Reservation, ...]:
        """予約の待ち行列（読み取り専用。先頭ほど早い予約）"""
        return tuple(self._reservations)

    def add_book(self, book: Book) -> None:
        if book.book_id in self._books:
            raise DuplicateBookError(book.book_id)
        self._books[book.book_id] = book

    def add_member(self, member: Member) -> None:
        if member.member_id in self._members:
            raise DuplicateMemberError(member.member_id)
        self._members[member.member_id] = member

    def borrow(self, member_id: str, book_id: str, today: date) -> Loan:
        member = self._get_member(member_id)
        book = self._get_book(book_id)
        self._settle_queue(book_id, today)  # 期限切れの取り置きを先に整理する

        check_can_borrow(
            member.policy,
            active_count=count_active_loans(self._loans, member_id),
            unpaid_fee=total_unpaid_fee(self._loans, member_id),
            available=is_book_available(self._loans, book_id),
            reserved_by_other=is_reserved_by_other(self._reservations, book_id, member_id),
        )

        loan = Loan(member, book, borrowed_on=today, due_on=calc_due_date(today, member.policy))
        self._loans.append(loan)
        self._remove_reservation(member_id, book_id)  # 自分の予約があれば消化
        return loan

    def return_book(self, book_id: str, today: date) -> Loan:
        self._get_book(book_id)
        index, loan = self._find_active_loan(book_id)

        late_fee = calc_late_fee(loan.due_on, today, loan.member.policy)
        closed = loan.closed(today, late_fee)
        self._loans[index] = closed
        self._settle_queue(book_id, today)  # 返却日から取り置き期限が始まる
        return closed

    def pay_fee(self, member_id: str) -> int:
        """未払いの延滞料をすべて支払い、支払った合計額を返す"""
        self._get_member(member_id)
        paid_total = total_unpaid_fee(self._loans, member_id)

        for i, loan in enumerate(self._loans):
            if loan.member.member_id == member_id and loan.has_unpaid_fee():
                self._loans[i] = loan.paid()
        return paid_total

    def reserve(self, member_id: str, book_id: str, today: date) -> Reservation:
        member = self._get_member(member_id)
        book = self._get_book(book_id)
        self._settle_queue(book_id, today)

        check_can_reserve(self._loans, self._reservations, book_id, member_id)

        reservation = Reservation(member, book, reserved_on=today)
        self._reservations.append(reservation)
        return reservation

    def cancel_reservation(self, member_id: str, book_id: str, today: date) -> Reservation:
        self._get_member(member_id)
        self._get_book(book_id)

        cancelled = self._remove_reservation(member_id, book_id)
        if cancelled is None:
            raise ReservationNotFoundError(member_id, book_id)
        self._settle_queue(book_id, today)  # 先頭が抜けたら次の人の取り置きが始まる
        return cancelled

    def _settle_queue(self, book_id: str, today: date) -> None:
        """その本の待ち行列を今日の時点に整える（期限切れの除去・取り置き期限の付与）"""
        queue = [r for r in self._reservations if r.book.book_id == book_id]
        others = [r for r in self._reservations if r.book.book_id != book_id]
        settled = settle_queue(queue, is_book_available(self._loans, book_id), today)
        self._reservations = others + settled

    def _remove_reservation(self, member_id: str, book_id: str) -> Reservation | None:
        for i, reservation in enumerate(self._reservations):
            if reservation.member.member_id == member_id and reservation.book.book_id == book_id:
                return self._reservations.pop(i)
        return None

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

    def new_library() -> Library:
        """本1冊と会員3人（太郎・花子・三郎）だけの、予約シナリオ用の図書館"""
        lib = Library()
        lib.add_book(Book("b1", "本1"))
        lib.add_member(Member("m1", "一般太郎", REGULAR))
        lib.add_member(Member("m2", "学生花子", STUDENT))
        lib.add_member(Member("m3", "一般三郎", REGULAR))
        return lib

    def after(base: date, days: int) -> date:
        return base + timedelta(days=days)

    print("【5】貸出中の本を予約し、返却後は先頭の予約者だけが借りられる")
    lib = new_library()
    lib.borrow("m1", "b1", today)
    attempt("花子が b1 を予約", lambda: lib.reserve("m2", "b1", today).reserved_on)
    attempt("三郎が b1 を予約", lambda: lib.reserve("m3", "b1", today).reserved_on)
    attempt("太郎が b1 を返却", lambda: lib.return_book("b1", after(today, 7)).late_fee)
    attempt("三郎が b1 を借りる（先頭は花子）", lambda: lib.borrow("m3", "b1", after(today, 7)))
    attempt("花子が b1 を借りる", lambda: lib.borrow("m2", "b1", after(today, 7)).due_on)

    print("【6】取り置きは返却から7日間。過ぎると予約は失効し、他の会員も借りられる")
    lib = new_library()
    lib.borrow("m1", "b1", today)
    lib.reserve("m2", "b1", today)
    returned = after(today, 3)
    attempt("太郎が b1 を返却", lambda: lib.return_book("b1", returned).late_fee)
    attempt(
        "三郎が借りる（返却の7日後=最終日）", lambda: lib.borrow("m3", "b1", after(returned, 7))
    )
    attempt(
        "三郎が借りる（返却の8日後=失効後）",
        lambda: lib.borrow("m3", "b1", after(returned, 8)).due_on,
    )


if __name__ == "__main__":
    demo()
