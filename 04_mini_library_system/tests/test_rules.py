from datetime import date

import pytest
from errors import BookUnavailableError, LoanLimitExceededError, UnpaidFeeError
from models import REGULAR, STUDENT, Book, Loan
from rules import (
    calc_due_date,
    calc_late_fee,
    check_can_borrow,
    count_active_loans,
    is_book_available,
    total_unpaid_fee,
)


@pytest.mark.parametrize(
    ("policy", "expected"),
    [(REGULAR, date(2026, 10, 15)), (STUDENT, date(2026, 10, 22))],
)
def test_返却期限は会員種別の貸出日数で決まる(policy, expected, borrowed_on):
    assert calc_due_date(borrowed_on, policy) == expected


class TestCalcLateFee:
    due_on = date(2026, 10, 15)

    @pytest.mark.parametrize(
        ("returned_on", "policy", "expected"),
        [
            (date(2026, 10, 10), REGULAR, 0),  # 期限前
            (date(2026, 10, 15), REGULAR, 0),  # 期限当日は延滞ではない
            (date(2026, 10, 16), REGULAR, 10),  # 1日延滞
            (date(2026, 10, 20), REGULAR, 50),  # 5日延滞（一般 10円/日）
            (date(2026, 10, 20), STUDENT, 25),  # 5日延滞（学生 5円/日）
        ],
    )
    def test_延滞料は延滞日数かける単価(self, returned_on, policy, expected):
        assert calc_late_fee(self.due_on, returned_on, policy) == expected


class TestLoansQueries:
    def test_貸出中の本は貸出可能でない(self, active_loan):
        assert not is_book_available([active_loan], "b1")

    def test_別の本は貸出可能(self, active_loan):
        assert is_book_available([active_loan], "b2")

    def test_返却済みなら貸出可能に戻る(self, active_loan):
        returned = active_loan.closed(date(2026, 10, 10), late_fee=0)
        assert is_book_available([returned], "b1")

    def test_貸出中の冊数は会員ごとに数える(self, regular_member, student_member, borrowed_on):
        loans = [
            Loan(regular_member, Book("b1", "A"), borrowed_on, date(2026, 10, 15)),
            Loan(regular_member, Book("b2", "B"), borrowed_on, date(2026, 10, 15)),
            Loan(student_member, Book("b3", "C"), borrowed_on, date(2026, 10, 22)),
        ]
        assert count_active_loans(loans, "m1") == 2
        assert count_active_loans(loans, "m2") == 1
        assert count_active_loans(loans, "m999") == 0

    def test_返却済みの本は貸出中の冊数に含めない(self, active_loan):
        returned = active_loan.closed(date(2026, 10, 10), late_fee=0)
        assert count_active_loans([returned], "m1") == 0

    def test_未払い延滞料は未払いのLoanだけ合計する(self, regular_member, borrowed_on):
        def loan(book_id: str) -> Loan:
            return Loan(regular_member, Book(book_id, book_id), borrowed_on, date(2026, 10, 15))

        unpaid_a = loan("b1").closed(date(2026, 10, 20), late_fee=50)
        unpaid_b = loan("b2").closed(date(2026, 10, 18), late_fee=30)
        paid = loan("b3").closed(date(2026, 10, 25), late_fee=100).paid()
        on_time = loan("b4").closed(date(2026, 10, 15), late_fee=0)
        still_active = loan("b5")

        loans = [unpaid_a, unpaid_b, paid, on_time, still_active]
        assert total_unpaid_fee(loans, "m1") == 80
        assert total_unpaid_fee(loans, "m2") == 0


class TestCheckCanBorrow:
    def test_問題なければ例外なし(self):
        check_can_borrow(REGULAR, active_count=2, unpaid_fee=0, available=True)

    def test_上限ちょうどまでは借りられない境界(self):
        # 一般は3冊まで。現在2冊なら3冊目はOK、3冊なら4冊目はNG
        check_can_borrow(REGULAR, active_count=2, unpaid_fee=0, available=True)
        with pytest.raises(LoanLimitExceededError):
            check_can_borrow(REGULAR, active_count=3, unpaid_fee=0, available=True)

    def test_学生は5冊まで借りられる(self):
        check_can_borrow(STUDENT, active_count=4, unpaid_fee=0, available=True)
        with pytest.raises(LoanLimitExceededError) as exc:
            check_can_borrow(STUDENT, active_count=5, unpaid_fee=0, available=True)
        assert (exc.value.max_loans, exc.value.current) == (5, 5)

    def test_貸出中の本は借りられない(self):
        with pytest.raises(BookUnavailableError):
            check_can_borrow(REGULAR, active_count=0, unpaid_fee=0, available=False)

    def test_延滞料が未払いなら借りられない(self):
        with pytest.raises(UnpaidFeeError) as exc:
            check_can_borrow(REGULAR, active_count=0, unpaid_fee=50, available=True)
        assert exc.value.unpaid_fee == 50

    def test_判定順は未払い_貸出中_上限の順(self):
        with pytest.raises(UnpaidFeeError):
            check_can_borrow(REGULAR, active_count=3, unpaid_fee=10, available=False)
        with pytest.raises(BookUnavailableError):
            check_can_borrow(REGULAR, active_count=3, unpaid_fee=0, available=False)
