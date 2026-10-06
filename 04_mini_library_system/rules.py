# 04_mini_library_system/rules.py
# 貸出ルールを表す純粋関数群。状態を持たず、「今日」も引数で受け取る。
from collections.abc import Iterable, Sequence
from dataclasses import replace
from datetime import date, timedelta

from errors import (
    AlreadyBorrowedError,
    BookAvailableError,
    BookReservedError,
    BookUnavailableError,
    DuplicateReservationError,
    LoanLimitExceededError,
    UnpaidFeeError,
)
from models import Loan, MembershipPolicy, Reservation

HOLD_DAYS = 7  # 返却された本を予約者のために取り置く日数


def calc_due_date(borrowed_on: date, policy: MembershipPolicy) -> date:
    """返却期限（ルール3）"""
    return borrowed_on + timedelta(days=policy.loan_days)


def calc_late_fee(due_on: date, returned_on: date, policy: MembershipPolicy) -> int:
    """延滞料 = 延滞日数 × 単価。期限内なら0円（ルール4）"""
    late_days = max(0, (returned_on - due_on).days)
    return late_days * policy.late_fee_per_day


def is_book_available(loans: Iterable[Loan], book_id: str) -> bool:
    """その本に貸出中の Loan がなければ貸出可能"""
    return not any(loan.book.book_id == book_id and loan.is_active() for loan in loans)


def count_active_loans(loans: Iterable[Loan], member_id: str) -> int:
    """会員が現在借りている冊数"""
    return sum(1 for loan in loans if loan.member.member_id == member_id and loan.is_active())


def total_unpaid_fee(loans: Iterable[Loan], member_id: str) -> int:
    """会員の未払い延滞料の合計"""
    return sum(
        loan.late_fee
        for loan in loans
        if loan.member.member_id == member_id and loan.has_unpaid_fee()
    )


def _queue(reservations: Iterable[Reservation], book_id: str) -> list[Reservation]:
    """その本の予約の待ち行列（先頭が最も早い予約）"""
    return [r for r in reservations if r.book.book_id == book_id]


def is_reserved_by_other(reservations: Iterable[Reservation], book_id: str, member_id: str) -> bool:
    """待ち行列の先頭が他の会員なら True。先頭の会員だけがその本を借りられる"""
    queue = _queue(reservations, book_id)
    return bool(queue) and queue[0].member.member_id != member_id


def check_can_borrow(
    policy: MembershipPolicy,
    active_count: int,
    unpaid_fee: int,
    available: bool,
    reserved_by_other: bool = False,
) -> None:
    """貸出可否の判定（ルール1・2・5と予約）。不可なら例外。

    判定順は 未払い → 他人の予約 → 貸出中 → 上限
    """
    if unpaid_fee > 0:
        raise UnpaidFeeError(unpaid_fee)
    if reserved_by_other:
        raise BookReservedError()
    if not available:
        raise BookUnavailableError()
    if active_count >= policy.max_loans:
        raise LoanLimitExceededError(policy.max_loans, active_count)


def check_can_reserve(
    loans: Iterable[Loan],
    reservations: Iterable[Reservation],
    book_id: str,
    member_id: str,
) -> None:
    """予約可否の判定。不可なら例外。

    予約できるのは「貸出中」または「予約者に取り置き中」の本だけ。
    判定順は 二重予約 → 自分が借りている → 借りられる本
    """
    loans = list(loans)
    queue = _queue(reservations, book_id)

    if any(r.member.member_id == member_id for r in queue):
        raise DuplicateReservationError(member_id, book_id)
    if any(
        loan.book.book_id == book_id and loan.member.member_id == member_id and loan.is_active()
        for loan in loans
    ):
        raise AlreadyBorrowedError(member_id, book_id)
    if is_book_available(loans, book_id) and not queue:
        raise BookAvailableError()


def settle_queue(
    queue: Sequence[Reservation],
    available: bool,
    today: date,
    hold_days: int = HOLD_DAYS,
) -> list[Reservation]:
    """1冊の本の待ち行列を今日の時点に整える（期限切れの除去と、取り置き期限の付与）。

    - 貸出中の間は取り置きは始まらず、そのまま返す
    - 貸出可能なら、先頭に今日から hold_days 日の期限を付ける
    - 先頭の期限が過ぎていたら行列から外し、次の人には「前の人の失効日」から期限を付ける
      （操作されるまで放置されても、失効日から順に連鎖して判定できる）
    """
    settled = list(queue)
    if not available:
        return settled

    start = today
    while settled:
        head = settled[0]
        if head.hold_until is None:
            head = replace(head, hold_until=start + timedelta(days=hold_days))
            settled[0] = head
        if head.hold_until >= today:
            break
        start = head.hold_until
        settled.pop(0)
    return settled


def settle_reservations(
    reservations: Iterable[Reservation],
    loans: Iterable[Loan],
    book_id: str,
    today: date,
) -> tuple[Reservation, ...]:
    """予約全体のうち、指定した本の待ち行列だけを今日の時点に整えて返す"""
    reservations = list(reservations)
    queue = _queue(reservations, book_id)
    others = [r for r in reservations if r.book.book_id != book_id]
    settled = settle_queue(queue, is_book_available(loans, book_id), today)
    return tuple(others + settled)


def remove_reservation(
    reservations: Iterable[Reservation], member_id: str, book_id: str
) -> tuple[tuple[Reservation, ...], Reservation | None]:
    """会員のその本への予約を外す。(外した後の予約, 外した予約 or None) を返す"""
    remaining = list(reservations)
    for i, reservation in enumerate(remaining):
        if reservation.member.member_id == member_id and reservation.book.book_id == book_id:
            return tuple(remaining[:i] + remaining[i + 1 :]), reservation
    return tuple(remaining), None
