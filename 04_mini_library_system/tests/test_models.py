from dataclasses import FrozenInstanceError
from datetime import date

import pytest
from models import REGULAR, STUDENT, Reservation


def test_会員種別の定数がルール通り():
    assert (REGULAR.max_loans, REGULAR.loan_days, REGULAR.late_fee_per_day) == (3, 14, 10)
    assert (STUDENT.max_loans, STUDENT.loan_days, STUDENT.late_fee_per_day) == (5, 21, 5)


def test_値オブジェクトは変更できない(active_loan):
    with pytest.raises(FrozenInstanceError):
        active_loan.late_fee = 100


class TestLoan:
    def test_生成直後は貸出中で延滞料なし(self, active_loan):
        assert active_loan.is_active()
        assert not active_loan.has_unpaid_fee()

    def test_closedは新しいLoanを返し元は変わらない(self, active_loan):
        closed = active_loan.closed(date(2026, 10, 20), late_fee=50)

        assert not closed.is_active()
        assert closed.returned_on == date(2026, 10, 20)
        assert closed.late_fee == 50
        assert active_loan.is_active()  # 元の Loan は貸出中のまま

    def test_延滞料ありで返却すると未払い状態になる(self, active_loan):
        assert active_loan.closed(date(2026, 10, 20), late_fee=50).has_unpaid_fee()

    def test_延滞なしで返却しても未払いにはならない(self, active_loan):
        assert not active_loan.closed(date(2026, 10, 15), late_fee=0).has_unpaid_fee()

    def test_paidで未払いが解消される(self, active_loan):
        paid = active_loan.closed(date(2026, 10, 20), late_fee=50).paid()

        assert paid.fee_paid
        assert not paid.has_unpaid_fee()

    def test_返却済みのLoanは再度closedできない(self, active_loan):
        closed = active_loan.closed(date(2026, 10, 15), late_fee=0)
        with pytest.raises(ValueError):
            closed.closed(date(2026, 10, 16), late_fee=0)

    def test_未払いがないLoanはpaidできない(self, active_loan):
        with pytest.raises(ValueError):
            active_loan.paid()


def test_Reservationは変更できない(regular_member, book):
    reservation = Reservation(regular_member, book, date(2026, 10, 1))
    assert reservation.reserved_on == date(2026, 10, 1)
    with pytest.raises(FrozenInstanceError):
        reservation.reserved_on = date(2026, 10, 2)


def test_Reservationのhold_untilは最初は未設定(regular_member, book):
    assert Reservation(regular_member, book, date(2026, 10, 1)).hold_until is None
