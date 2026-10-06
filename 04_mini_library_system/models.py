# 04_mini_library_system/models.py
from dataclasses import dataclass, replace
from datetime import date


# MembershipPolicy (会員種別ごとの違いを数値で表す値オブジェクト)
@dataclass(frozen=True)
class MembershipPolicy:
    name: str
    max_loans: int
    loan_days: int
    late_fee_per_day: int


REGULAR = MembershipPolicy(name="一般", max_loans=3, loan_days=14, late_fee_per_day=10)
STUDENT = MembershipPolicy(name="学生", max_loans=5, loan_days=21, late_fee_per_day=5)


@dataclass(frozen=True)
class Book:
    """蔵書1冊（同じタイトルでもコピー単位で区別する）"""

    book_id: str
    title: str


@dataclass(frozen=True)
class Member:
    member_id: str
    name: str
    policy: MembershipPolicy


# Loan (貸出記録 / イミュータブル。状態の変化は新しい Loan を返して表現する)
@dataclass(frozen=True)
class Loan:
    member: Member
    book: Book
    borrowed_on: date
    due_on: date
    returned_on: date | None = None
    late_fee: int = 0
    fee_paid: bool = False

    def is_active(self) -> bool:
        """貸出中（まだ返却されていない）"""
        return self.returned_on is None

    def has_unpaid_fee(self) -> bool:
        """返却済みで、延滞料が未払い"""
        return not self.is_active() and self.late_fee > 0 and not self.fee_paid

    def closed(self, today: date, late_fee: int) -> "Loan":
        """返却済みの新しい Loan を返す"""
        if not self.is_active():
            raise ValueError("すでに返却済みの Loan です")
        return replace(self, returned_on=today, late_fee=late_fee)

    def paid(self) -> "Loan":
        """延滞料支払済みの新しい Loan を返す"""
        if not self.has_unpaid_fee():
            raise ValueError("未払いの延滞料がありません")
        return replace(self, fee_paid=True)
