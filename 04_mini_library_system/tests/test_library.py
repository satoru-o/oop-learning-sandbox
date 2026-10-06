from datetime import date, timedelta

import pytest
from errors import (
    AlreadyBorrowedError,
    BookAvailableError,
    BookNotFoundError,
    BookNotOnLoanError,
    BookReservedError,
    BookUnavailableError,
    DuplicateBookError,
    DuplicateMemberError,
    DuplicateReservationError,
    LoanLimitExceededError,
    MemberNotFoundError,
    ReservationNotFoundError,
    UnpaidFeeError,
)
from late_fee import CappedLateFee, PerDayLateFee, WeekendFreeLateFee
from library import Library
from models import REGULAR, STUDENT, Book, Member
from repository import InMemoryRepository

TODAY = date(2026, 10, 1)


@pytest.fixture
def library(regular_member, student_member) -> Library:
    lib = Library()
    for i in range(1, 7):
        lib.add_book(Book(f"b{i}", f"本{i}"))
    lib.add_member(regular_member)  # m1: 一般
    lib.add_member(student_member)  # m2: 学生
    lib.add_member(Member("m3", "一般三郎", REGULAR))  # m3: 一般
    return lib


class TestRegister:
    def test_同じIDの本は登録できない(self, library):
        with pytest.raises(DuplicateBookError) as exc:
            library.add_book(Book("b1", "別のタイトル"))
        assert exc.value.book_id == "b1"

    def test_中身が完全に同じ本でも二重登録はできない(self, library):
        with pytest.raises(DuplicateBookError):
            library.add_book(Book("b1", "本1"))

    def test_同じIDの会員は登録できない(self, library):
        with pytest.raises(DuplicateMemberError) as exc:
            library.add_member(Member("m1", "別人", STUDENT))
        assert exc.value.member_id == "m1"

    def test_重複で拒否されても元の登録は変わらない(self, library):
        with pytest.raises(DuplicateBookError):
            library.add_book(Book("b1", "別のタイトル"))
        with pytest.raises(DuplicateMemberError):
            library.add_member(Member("m1", "別人", STUDENT))

        loan = library.borrow("m1", "b1", TODAY)
        assert loan.book.title == "本1"
        assert loan.member.name == "一般太郎"
        assert loan.member.policy == REGULAR

    def test_別IDなら登録できる(self, library):
        library.add_book(Book("b100", "新しい本"))
        library.add_member(Member("m100", "新会員", REGULAR))
        library.borrow("m100", "b100", TODAY)


class TestBorrow:
    def test_借りるとLoanが返り_期限は会員種別で決まる(self, library):
        loan = library.borrow("m1", "b1", TODAY)
        assert (loan.member.member_id, loan.book.book_id) == ("m1", "b1")
        assert loan.borrowed_on == TODAY
        assert loan.due_on == date(2026, 10, 15)  # 一般 14日

        assert library.borrow("m2", "b2", TODAY).due_on == date(2026, 10, 22)  # 学生 21日

    def test_存在しない会員や本は借りられない(self, library):
        with pytest.raises(MemberNotFoundError):
            library.borrow("m999", "b1", TODAY)
        with pytest.raises(BookNotFoundError):
            library.borrow("m1", "b999", TODAY)

    def test_貸出中の本は他の会員が借りられない(self, library):
        library.borrow("m1", "b1", TODAY)
        with pytest.raises(BookUnavailableError):
            library.borrow("m2", "b1", TODAY)

    def test_一般会員は4冊目を借りられない(self, library):
        for book_id in ("b1", "b2", "b3"):
            library.borrow("m1", book_id, TODAY)
        with pytest.raises(LoanLimitExceededError):
            library.borrow("m1", "b4", TODAY)

    def test_学生は5冊まで借りられる(self, library):
        for book_id in ("b1", "b2", "b3", "b4", "b5"):
            library.borrow("m2", book_id, TODAY)
        with pytest.raises(LoanLimitExceededError):
            library.borrow("m2", "b6", TODAY)

    def test_失敗した貸出は記録に残らない(self, library):
        library.borrow("m1", "b1", TODAY)
        with pytest.raises(BookUnavailableError):
            library.borrow("m2", "b1", TODAY)
        assert len(library.loans) == 1


class TestReturn:
    def test_期限内の返却は延滞料なしで_本が貸出可能に戻る(self, library):
        library.borrow("m1", "b1", TODAY)
        loan = library.return_book("b1", date(2026, 10, 15))

        assert not loan.is_active()
        assert loan.late_fee == 0
        library.borrow("m2", "b1", date(2026, 10, 16))  # 借りられる

    @pytest.mark.parametrize(("member_id", "fee"), [("m1", 50), ("m2", 25)])
    def test_期限を5日過ぎると延滞料が発生する(self, library, member_id, fee):
        loan = library.borrow(member_id, "b1", TODAY)
        returned = library.return_book("b1", loan.due_on + timedelta(days=5))
        assert returned.late_fee == fee

    def test_返却するとloansの記録が返却済みに置き換わる(self, library):
        library.borrow("m1", "b1", TODAY)
        library.return_book("b1", TODAY)
        assert len(library.loans) == 1
        assert not library.loans[0].is_active()

    def test_貸出中でない本は返却できない(self, library):
        with pytest.raises(BookNotOnLoanError):
            library.return_book("b1", TODAY)
        with pytest.raises(BookNotFoundError):
            library.return_book("b999", TODAY)

    def test_同じ本を二度返却できない(self, library):
        library.borrow("m1", "b1", TODAY)
        library.return_book("b1", TODAY)
        with pytest.raises(BookNotOnLoanError):
            library.return_book("b1", TODAY)


class TestPayFee:
    @pytest.fixture
    def overdue_library(self, library) -> Library:
        """m1 が5日延滞して返却済み（未払い50円）の状態"""
        library.borrow("m1", "b1", TODAY)
        library.return_book("b1", date(2026, 10, 20))
        return library

    def test_延滞料が未払いの間は借りられない(self, overdue_library):
        with pytest.raises(UnpaidFeeError) as exc:
            overdue_library.borrow("m1", "b2", date(2026, 10, 21))
        assert exc.value.unpaid_fee == 50

    def test_他の会員には影響しない(self, overdue_library):
        overdue_library.borrow("m2", "b2", date(2026, 10, 21))

    def test_支払うと支払った合計額が返り_再び借りられる(self, overdue_library):
        assert overdue_library.pay_fee("m1") == 50
        overdue_library.borrow("m1", "b2", date(2026, 10, 21))

    def test_未払いがなければ0円(self, library):
        assert library.pay_fee("m1") == 0

    def test_複数の未払いはまとめて支払う(self, library):
        library.borrow("m1", "b1", TODAY)
        library.borrow("m1", "b2", TODAY)
        library.return_book("b1", date(2026, 10, 20))  # 5日延滞 = 50円
        library.return_book("b2", date(2026, 10, 17))  # 2日延滞 = 20円
        assert library.pay_fee("m1") == 70
        assert library.pay_fee("m1") == 0

    def test_存在しない会員は支払えない(self, library):
        with pytest.raises(MemberNotFoundError):
            library.pay_fee("m999")


class TestReserve:
    @pytest.fixture
    def on_loan(self, library) -> Library:
        """m1 が b1 を借りている状態"""
        library.borrow("m1", "b1", TODAY)
        return library

    def test_貸出中の本を予約できる(self, on_loan):
        reservation = on_loan.reserve("m2", "b1", TODAY)
        assert (reservation.member.member_id, reservation.book.book_id) == ("m2", "b1")
        assert reservation.reserved_on == TODAY
        assert on_loan.reservations == (reservation,)

    def test_借りられる本は予約できない(self, library):
        with pytest.raises(BookAvailableError):
            library.reserve("m1", "b1", TODAY)

    def test_二重予約や自分が借りている本の予約はできない(self, on_loan):
        on_loan.reserve("m2", "b1", TODAY)
        with pytest.raises(DuplicateReservationError):
            on_loan.reserve("m2", "b1", TODAY)
        with pytest.raises(AlreadyBorrowedError):
            on_loan.reserve("m1", "b1", TODAY)

    def test_存在しない会員や本は予約できない(self, on_loan):
        with pytest.raises(MemberNotFoundError):
            on_loan.reserve("m999", "b1", TODAY)
        with pytest.raises(BookNotFoundError):
            on_loan.reserve("m2", "b999", TODAY)

    def test_失敗した予約は記録に残らない(self, library):
        with pytest.raises(BookAvailableError):
            library.reserve("m1", "b1", TODAY)
        assert library.reservations == ()

    def test_返却後は予約者以外は借りられず_予約者は借りられる(self, on_loan):
        on_loan.reserve("m2", "b1", TODAY)
        on_loan.return_book("b1", TODAY)

        with pytest.raises(BookReservedError):
            on_loan.borrow("m3", "b1", TODAY)
        loan = on_loan.borrow("m2", "b1", TODAY)
        assert loan.member.member_id == "m2"

    def test_借りると予約は消化される(self, on_loan):
        on_loan.reserve("m2", "b1", TODAY)
        on_loan.return_book("b1", TODAY)
        on_loan.borrow("m2", "b1", TODAY)
        assert on_loan.reservations == ()

    def test_予約は先着順に消化される(self, on_loan):
        on_loan.reserve("m2", "b1", TODAY)
        on_loan.reserve("m3", "b1", TODAY)  # 取り置き前でも3人目として並べる

        on_loan.return_book("b1", TODAY)
        with pytest.raises(BookReservedError):
            on_loan.borrow("m3", "b1", TODAY)  # 先頭は m2
        on_loan.borrow("m2", "b1", TODAY)

        on_loan.return_book("b1", TODAY)
        on_loan.borrow("m3", "b1", TODAY)  # 次は m3
        assert on_loan.reservations == ()

    def test_予約者でも貸出中の間は借りられない(self, on_loan):
        on_loan.reserve("m2", "b1", TODAY)
        with pytest.raises(BookUnavailableError):
            on_loan.borrow("m2", "b1", TODAY)

    def test_予約は他の本の貸出に影響しない(self, on_loan):
        on_loan.reserve("m2", "b1", TODAY)
        on_loan.borrow("m3", "b2", TODAY)

    def test_取り置き中の本は他の会員がさらに予約できる(self, on_loan):
        on_loan.reserve("m2", "b1", TODAY)
        on_loan.return_book("b1", TODAY)  # 貸出可能だが m2 に取り置き
        on_loan.reserve("m3", "b1", TODAY)
        assert [r.member.member_id for r in on_loan.reservations] == ["m2", "m3"]

    def test_借りるのに失敗したら予約は消化されない(self, on_loan):
        on_loan.reserve("m2", "b1", TODAY)
        # m2 を延滞料の未払い状態にする（学生: 期限10/22 → 2日延滞 = 10円）
        on_loan.borrow("m2", "b2", TODAY)
        on_loan.return_book("b2", date(2026, 10, 24))
        on_loan.return_book("b1", date(2026, 10, 24))

        with pytest.raises(UnpaidFeeError):
            on_loan.borrow("m2", "b1", date(2026, 10, 24))
        assert len(on_loan.reservations) == 1


def day(n: int) -> date:
    """基準日(TODAY)から n 日後"""
    return TODAY + timedelta(days=n)


class TestHoldExpiry:
    """取り置き期限は、返却された日から7日間（7日目までは借りられる）"""

    @pytest.fixture
    def reserved(self, library) -> Library:
        """m1 が b1 を借り、m2・m3 がこの順で予約している状態"""
        library.borrow("m1", "b1", TODAY)
        library.reserve("m2", "b1", TODAY)
        library.reserve("m3", "b1", TODAY)
        return library

    def test_貸出中の間は取り置き期限が付かない(self, reserved):
        assert [r.hold_until for r in reserved.reservations] == [None, None]

    def test_返却すると先頭に返却日から7日の期限が付く(self, reserved):
        reserved.return_book("b1", day(20))  # 延滞して返却しても、起点は返却日
        assert [r.hold_until for r in reserved.reservations] == [day(27), None]

    def test_7日目までは予約者が借りられる(self, reserved):
        reserved.return_book("b1", day(3))
        reserved.borrow("m2", "b1", day(10))

    def test_期限切れで次の予約者に取り置きが移る(self, reserved):
        reserved.return_book("b1", day(3))
        with pytest.raises(BookReservedError):
            reserved.borrow("m3", "b1", day(10))  # 10日目: まだ m2 の取り置き中

        reserved.borrow("m3", "b1", day(11))  # 11日目: m2 は失効し、m3 の取り置きは 17日目まで

    def test_期限切れの予約者は優先権を失い_行列から外れる(self, reserved):
        reserved.return_book("b1", day(3))
        reserved.borrow("m3", "b1", day(11))
        assert reserved.reservations == ()  # m2 は失効、m3 は消化済み

    def test_全員が失効すれば誰でも借りられる(self, library):
        library.borrow("m1", "b1", TODAY)
        library.reserve("m2", "b1", TODAY)
        library.return_book("b1", day(3))
        library.borrow("m3", "b1", day(11))  # 予約者でない m3 が借りられる

    def test_期限切れの予約者も通常の貸出としては借りられる(self, library):
        library.borrow("m1", "b1", TODAY)
        library.reserve("m2", "b1", TODAY)
        library.return_book("b1", day(3))
        library.borrow("m2", "b1", day(11))

    def test_未払いで借りられない先頭は期限切れで次の人に譲る(self, library):
        library.borrow("m2", "b2", TODAY)
        library.return_book("b2", day(24))  # m2: 学生の期限21日 + 3日延滞 = 15円
        library.borrow("m1", "b1", day(24))
        library.reserve("m2", "b1", day(24))
        library.reserve("m3", "b1", day(24))
        library.return_book("b1", day(25))

        with pytest.raises(UnpaidFeeError):
            library.borrow("m2", "b1", day(26))
        library.borrow("m3", "b1", day(33))  # m2 の期限(32日目)が切れた翌日

    def test_先頭がキャンセルすると次の人はキャンセル日から7日間(self, reserved):
        reserved.return_book("b1", day(3))
        reserved.cancel_reservation("m2", "b1", day(5))
        assert [r.hold_until for r in reserved.reservations] == [day(12)]

    def test_貸出中に先頭がキャンセルしても期限は始まらない(self, reserved):
        reserved.cancel_reservation("m2", "b1", day(5))
        assert [r.hold_until for r in reserved.reservations] == [None]

    def test_予約は他の本の取り置き期限に影響しない(self, reserved):
        reserved.borrow("m1", "b2", TODAY)
        reserved.reserve("m3", "b2", TODAY)
        reserved.return_book("b1", day(3))
        by_book: dict[str, list[date | None]] = {}
        for r in reserved.reservations:
            by_book.setdefault(r.book.book_id, []).append(r.hold_until)
        assert by_book == {"b1": [day(10), None], "b2": [None]}


class TestCancelReservation:
    def test_キャンセルすると待ち行列から外れる(self, library):
        library.borrow("m1", "b1", TODAY)
        library.reserve("m2", "b1", TODAY)

        cancelled = library.cancel_reservation("m2", "b1", TODAY)
        assert cancelled.member.member_id == "m2"
        assert library.reservations == ()

    def test_キャンセル後は次の人が借りられる(self, library):
        library.borrow("m1", "b1", TODAY)
        library.reserve("m2", "b1", TODAY)
        library.reserve("m3", "b1", TODAY)
        library.return_book("b1", TODAY)

        library.cancel_reservation("m2", "b1", TODAY)
        library.borrow("m3", "b1", TODAY)

    def test_予約がなければキャンセルできない(self, library):
        with pytest.raises(ReservationNotFoundError):
            library.cancel_reservation("m2", "b1", TODAY)

    def test_存在しない会員や本はキャンセルできない(self, library):
        with pytest.raises(MemberNotFoundError):
            library.cancel_reservation("m999", "b1", TODAY)
        with pytest.raises(BookNotFoundError):
            library.cancel_reservation("m2", "b999", TODAY)


def test_loansは読み取り専用のtuple(library):
    library.borrow("m1", "b1", TODAY)
    assert isinstance(library.loans, tuple)


def test_reservationsは読み取り専用のtuple(library):
    library.borrow("m1", "b1", TODAY)
    library.reserve("m2", "b1", TODAY)
    assert isinstance(library.reservations, tuple)


class TestLateFeeRule:
    """延滞料ルールの差し替え。TODAY(10/1・木曜)に借りると、一般は10/15・学生は10/22(どちらも木曜)が期限"""

    @staticmethod
    def _library(rule=None, repository=None) -> Library:
        lib = Library(repository, late_fee_rule=rule)
        if not lib.state.books:
            lib.add_book(Book("b1", "本1"))
            lib.add_member(Member("m1", "一般太郎", REGULAR))
            lib.add_member(Member("m2", "学生花子", STUDENT))
        return lib

    @staticmethod
    def _return_late(lib: Library, member_id: str, days_late: int) -> int:
        loan = lib.borrow(member_id, "b1", TODAY)
        return lib.return_book("b1", loan.due_on + timedelta(days=days_late)).late_fee

    def test_何も指定しなければ日数かける単価(self):
        assert self._return_late(self._library(), "m1", 7) == 70

    def test_PerDayLateFeeを明示しても同じ(self):
        assert self._return_late(self._library(PerDayLateFee()), "m1", 7) == 70

    def test_土日免除では土日を数えない(self):
        assert self._return_late(self._library(WeekendFreeLateFee()), "m1", 7) == 50

    def test_上限額を超えない(self):
        assert self._return_late(self._library(CappedLateFee(PerDayLateFee(), 60)), "m1", 7) == 60

    def test_会員種別の単価が使われる(self):
        rule = WeekendFreeLateFee()
        assert self._return_late(self._library(rule), "m2", 7) == 25  # 学生 5円 × 平日5日

    def test_組み合わせたルールも使える(self):
        rule = CappedLateFee(WeekendFreeLateFee(), cap=40)
        assert self._return_late(self._library(rule), "m1", 7) == 40

    def test_未払い額と支払い額にもルールが反映される(self):
        lib = self._library(WeekendFreeLateFee())
        self._return_late(lib, "m1", 7)

        with pytest.raises(UnpaidFeeError) as exc:
            lib.borrow("m1", "b1", day(40))
        assert exc.value.unpaid_fee == 50
        assert lib.pay_fee("m1") == 50

    def test_ルールを変えても確定済みの延滞料は変わらない(self):
        repo = InMemoryRepository()
        self._return_late(self._library(repository=repo), "m1", 7)  # 標準ルールで 70円

        restarted = self._library(WeekendFreeLateFee(), repository=repo)  # 再起動後にルール変更
        assert restarted.pay_fee("m1") == 70
