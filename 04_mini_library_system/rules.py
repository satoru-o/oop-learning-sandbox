# 04_mini_library_system/rules.py
# 貸出ルールを表す純粋関数群。状態を持たず、「今日」も引数で受け取る。
from collections.abc import Iterable
from datetime import date, timedelta

from errors import BookUnavailableError, LoanLimitExceededError, UnpaidFeeError
from models import Loan, MembershipPolicy


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


def check_can_borrow(
    policy: MembershipPolicy,
    active_count: int,
    unpaid_fee: int,
    available: bool,
) -> None:
    """貸出可否の判定（ルール1・2・5）。不可なら例外。判定順は 未払い → 貸出中 → 上限"""
    if unpaid_fee > 0:
        raise UnpaidFeeError(unpaid_fee)
    if not available:
        raise BookUnavailableError()
    if active_count >= policy.max_loans:
        raise LoanLimitExceededError(policy.max_loans, active_count)
