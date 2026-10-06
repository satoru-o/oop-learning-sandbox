from dataclasses import replace
from datetime import date, timedelta

import pytest
from errors import (
    AlreadyBorrowedError,
    BookAvailableError,
    BookReservedError,
    BookUnavailableError,
    DuplicateReservationError,
    LoanLimitExceededError,
    UnpaidFeeError,
)
from models import REGULAR, STUDENT, Book, Loan, Member, Reservation
from rules import (
    calc_due_date,
    calc_late_fee,
    check_can_borrow,
    check_can_reserve,
    count_active_loans,
    is_book_available,
    is_reserved_by_other,
    remove_reservation,
    settle_queue,
    settle_reservations,
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


def _reservation(member_id: str, book_id: str = "b1") -> Reservation:
    return Reservation(
        Member(member_id, member_id, REGULAR), Book(book_id, book_id), date(2026, 10, 1)
    )


class TestIsReservedByOther:
    def test_予約がなければFalse(self):
        assert not is_reserved_by_other([], "b1", "m1")

    def test_先頭が他の会員ならTrue(self):
        assert is_reserved_by_other([_reservation("m2")], "b1", "m1")

    def test_先頭が自分ならFalse(self):
        assert not is_reserved_by_other([_reservation("m1"), _reservation("m2")], "b1", "m1")

    def test_自分が予約していても先頭でなければTrue(self):
        assert is_reserved_by_other([_reservation("m2"), _reservation("m1")], "b1", "m1")

    def test_別の本の予約は関係ない(self):
        assert not is_reserved_by_other([_reservation("m2", "b2")], "b1", "m1")


class TestCheckCanBorrowWithReservation:
    def test_他人が先に予約していると借りられない(self):
        with pytest.raises(BookReservedError):
            check_can_borrow(
                REGULAR, active_count=0, unpaid_fee=0, available=True, reserved_by_other=True
            )

    def test_判定順は未払い_予約_貸出中_上限(self):
        with pytest.raises(UnpaidFeeError):
            check_can_borrow(REGULAR, 3, 10, False, reserved_by_other=True)
        with pytest.raises(BookReservedError):
            check_can_borrow(REGULAR, 3, 0, False, reserved_by_other=True)

    def test_reserved_by_otherを省略すれば従来どおり(self):
        check_can_borrow(REGULAR, active_count=0, unpaid_fee=0, available=True)


class TestCheckCanReserve:
    def test_貸出中の本は予約できる(self, active_loan):
        check_can_reserve([active_loan], [], "b1", "m2")

    def test_取り置き中の本は3人目も予約できる(self):
        # 本は返却済み（貸出可能）だが、m2 が予約済みで取り置かれている
        check_can_reserve([], [_reservation("m2")], "b1", "m3")

    def test_借りられる本は予約できない(self):
        with pytest.raises(BookAvailableError):
            check_can_reserve([], [], "b1", "m1")

    def test_同じ本の二重予約はできない(self, active_loan):
        with pytest.raises(DuplicateReservationError):
            check_can_reserve([active_loan], [_reservation("m2")], "b1", "m2")

    def test_自分が借りている本は予約できない(self, active_loan):
        with pytest.raises(AlreadyBorrowedError):
            check_can_reserve([active_loan], [], "b1", "m1")


def _day(n: int) -> date:
    """基準日(2026-10-01)から n 日後"""
    return date(2026, 10, 1) + timedelta(days=n)


def _held(member_id: str, until: date | None) -> Reservation:
    return replace(_reservation(member_id), hold_until=until)


class TestSettleQueue:
    def test_空の待ち行列は空のまま(self):
        assert settle_queue([], available=True, today=_day(0)) == []

    def test_貸出中の間は取り置きが始まらない(self):
        queue = [_held("m1", None), _held("m2", None)]
        assert settle_queue(queue, available=False, today=_day(0)) == queue

    def test_貸出可能になると先頭に7日間の取り置き期限が付く(self):
        queue = [_held("m1", None), _held("m2", None)]
        settled = settle_queue(queue, available=True, today=_day(0))

        assert [r.hold_until for r in settled] == [_day(7), None]
        assert [r.member.member_id for r in settled] == ["m1", "m2"]

    def test_取り置き期限の当日までは有効(self):
        queue = [_held("m1", _day(7)), _held("m2", None)]
        assert settle_queue(queue, available=True, today=_day(7)) == queue

    def test_期限を過ぎると失効し_次の人は失効日から7日間(self):
        queue = [_held("m1", _day(7)), _held("m2", None)]
        settled = settle_queue(queue, available=True, today=_day(8))

        assert [r.member.member_id for r in settled] == ["m2"]
        assert settled[0].hold_until == _day(14)

    def test_何日も放置されても失効日から順に連鎖して判定する(self):
        # m1: 7日目 / m2: 14日目 / m3: 21日目 まで。15日目に判定すると m3 が取り置き中
        queue = [_held("m1", _day(7)), _held("m2", None), _held("m3", None)]
        settled = settle_queue(queue, available=True, today=_day(15))

        assert [r.member.member_id for r in settled] == ["m3"]
        assert settled[0].hold_until == _day(21)

    def test_全員失効すれば空になる(self):
        queue = [_held("m1", _day(7)), _held("m2", None)]
        assert settle_queue(queue, available=True, today=_day(30)) == []

    def test_元の待ち行列は変更しない(self):
        queue = [_held("m1", None)]
        settle_queue(queue, available=True, today=_day(0))
        assert queue[0].hold_until is None


class TestSettleReservations:
    def test_対象の本の待ち行列だけを整える(self):
        reservations = (_held("m1", None), _reservation("m2", "b2"))
        settled = settle_reservations(reservations, loans=[], book_id="b1", today=_day(0))

        by_book = {r.book.book_id: r.hold_until for r in settled}
        assert by_book == {"b1": _day(7), "b2": None}  # b2 は触らない

    def test_貸出中の本は取り置きが始まらない(self, active_loan):
        reservations = (_held("m2", None),)
        settled = settle_reservations(reservations, [active_loan], "b1", _day(0))
        assert settled == reservations

    def test_期限切れは取り除かれる(self):
        reservations = (_held("m1", _day(7)),)
        assert settle_reservations(reservations, [], "b1", _day(8)) == ()

    def test_結果はtuple(self):
        assert isinstance(settle_reservations([], [], "b1", _day(0)), tuple)


class TestRemoveReservation:
    def test_該当の予約を外して返す(self):
        a, b = _reservation("m1"), _reservation("m2")
        remaining, removed = remove_reservation((a, b), "m1", "b1")
        assert remaining == (b,)
        assert removed == a

    def test_該当がなければそのままNone(self):
        reservations = (_reservation("m1"),)
        remaining, removed = remove_reservation(reservations, "m2", "b1")
        assert remaining == reservations
        assert removed is None

    def test_別の本の予約は外さない(self):
        reservations = (_reservation("m1", "b2"),)
        remaining, removed = remove_reservation(reservations, "m1", "b1")
        assert remaining == reservations
        assert removed is None
