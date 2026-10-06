# 04_mini_library_system/library.py
# 状態を持つ「殻」。判定・計算は rules.py の純粋関数に任せ、
# 「新しい LibraryState を計算 → Repository に保存 → 差し替え」の順で状態を更新する。
from dataclasses import replace
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
from repository import InMemoryRepository, LibraryRepository
from rules import (
    calc_due_date,
    calc_late_fee,
    check_can_borrow,
    check_can_reserve,
    count_active_loans,
    is_book_available,
    is_reserved_by_other,
    remove_reservation,
    settle_reservations,
    total_unpaid_fee,
)
from state import LibraryState


class Library:
    def __init__(self, repository: LibraryRepository | None = None):
        self._repository = repository if repository is not None else InMemoryRepository()
        self._state = self._repository.load()

    @property
    def state(self) -> LibraryState:
        """現在の状態（イミュータブルなスナップショット）"""
        return self._state

    @property
    def loans(self) -> tuple[Loan, ...]:
        """貸出記録（読み取り専用）"""
        return self._state.loans

    @property
    def reservations(self) -> tuple[Reservation, ...]:
        """予約の待ち行列（読み取り専用。先頭ほど早い予約）"""
        return self._state.reservations

    def add_book(self, book: Book) -> None:
        if any(b.book_id == book.book_id for b in self._state.books):
            raise DuplicateBookError(book.book_id)
        self._commit(replace(self._state, books=self._state.books + (book,)))

    def add_member(self, member: Member) -> None:
        if any(m.member_id == member.member_id for m in self._state.members):
            raise DuplicateMemberError(member.member_id)
        self._commit(replace(self._state, members=self._state.members + (member,)))

    def borrow(self, member_id: str, book_id: str, today: date) -> Loan:
        state = self._state
        member = self._get_member(member_id)
        book = self._get_book(book_id)
        # 期限切れの取り置きを先に整理する（この結果は、操作が成功したときだけ反映される）
        reservations = settle_reservations(state.reservations, state.loans, book_id, today)

        check_can_borrow(
            member.policy,
            active_count=count_active_loans(state.loans, member_id),
            unpaid_fee=total_unpaid_fee(state.loans, member_id),
            available=is_book_available(state.loans, book_id),
            reserved_by_other=is_reserved_by_other(reservations, book_id, member_id),
        )

        loan = Loan(member, book, borrowed_on=today, due_on=calc_due_date(today, member.policy))
        reservations, _ = remove_reservation(reservations, member_id, book_id)  # 予約を消化
        self._commit(replace(state, loans=state.loans + (loan,), reservations=reservations))
        return loan

    def return_book(self, book_id: str, today: date) -> Loan:
        state = self._state
        self._get_book(book_id)
        index, loan = self._find_active_loan(book_id)

        late_fee = calc_late_fee(loan.due_on, today, loan.member.policy)
        closed = loan.closed(today, late_fee)
        loans = state.loans[:index] + (closed,) + state.loans[index + 1 :]
        # 返却日から取り置き期限が始まる
        reservations = settle_reservations(state.reservations, loans, book_id, today)
        self._commit(replace(state, loans=loans, reservations=reservations))
        return closed

    def pay_fee(self, member_id: str) -> int:
        """未払いの延滞料をすべて支払い、支払った合計額を返す"""
        state = self._state
        self._get_member(member_id)
        paid_total = total_unpaid_fee(state.loans, member_id)
        if paid_total == 0:
            return 0

        loans = tuple(
            loan.paid() if loan.member.member_id == member_id and loan.has_unpaid_fee() else loan
            for loan in state.loans
        )
        self._commit(replace(state, loans=loans))
        return paid_total

    def reserve(self, member_id: str, book_id: str, today: date) -> Reservation:
        state = self._state
        member = self._get_member(member_id)
        book = self._get_book(book_id)
        reservations = settle_reservations(state.reservations, state.loans, book_id, today)

        check_can_reserve(state.loans, reservations, book_id, member_id)

        reservation = Reservation(member, book, reserved_on=today)
        self._commit(replace(state, reservations=reservations + (reservation,)))
        return reservation

    def cancel_reservation(self, member_id: str, book_id: str, today: date) -> Reservation:
        state = self._state
        self._get_member(member_id)
        self._get_book(book_id)

        remaining, cancelled = remove_reservation(state.reservations, member_id, book_id)
        if cancelled is None:
            raise ReservationNotFoundError(member_id, book_id)
        # 先頭が抜けたら次の人の取り置きが始まる
        reservations = settle_reservations(remaining, state.loans, book_id, today)
        self._commit(replace(state, reservations=reservations))
        return cancelled

    def _commit(self, new_state: LibraryState) -> None:
        """保存に成功してから状態を差し替える（保存に失敗したらメモリも変えない）"""
        self._repository.save(new_state)
        self._state = new_state

    def _get_member(self, member_id: str) -> Member:
        for member in self._state.members:
            if member.member_id == member_id:
                return member
        raise MemberNotFoundError(member_id)

    def _get_book(self, book_id: str) -> Book:
        for book in self._state.books:
            if book.book_id == book_id:
                return book
        raise BookNotFoundError(book_id)

    def _find_active_loan(self, book_id: str) -> tuple[int, Loan]:
        for i, loan in enumerate(self._state.loans):
            if loan.book.book_id == book_id and loan.is_active():
                return i, loan
        raise BookNotOnLoanError(book_id)


def demo() -> None:
    import tempfile
    from datetime import timedelta
    from pathlib import Path

    from errors import LibraryError, StorageError
    from models import REGULAR, STUDENT
    from repository import JsonFileRepository

    today = date(2026, 10, 1)
    library = Library()
    for i in range(1, 6):
        library.add_book(Book(f"b{i}", f"本{i}"))
    library.add_member(Member("m1", "一般太郎", REGULAR))
    library.add_member(Member("m2", "学生花子", STUDENT))

    def attempt(label: str, action) -> None:
        try:
            result = action()
        except (LibraryError, StorageError) as e:
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

    def new_library(repository=None) -> Library:
        """本1冊と会員3人（太郎・花子・三郎）だけの、予約・保存シナリオ用の図書館"""
        lib = Library(repository)
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

    print("【7】JSONファイルに保存し、再起動したつもりで続きから使う")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "library.json"
        first = new_library(JsonFileRepository(path))
        first.borrow("m1", "b1", today)
        first.reserve("m2", "b1", today)
        print(f"  ✓ 保存した: {path.name}（{path.stat().st_size} バイト）")

        second = Library(JsonFileRepository(path))  # 再起動
        attempt(
            "読み込んだ（貸出, 予約）の数", lambda: (len(second.loans), len(second.reservations))
        )
        attempt("太郎が b1 を返却", lambda: second.return_book("b1", after(today, 3)).late_fee)
        attempt(
            "花子が b1 を借りる（予約も引き継がれている）",
            lambda: second.borrow("m2", "b1", after(today, 3)).due_on,
        )

        path.write_text("{ broken", encoding="utf-8")
        attempt("壊れたファイルで起動", lambda: Library(JsonFileRepository(path)))


if __name__ == "__main__":
    demo()
