from datetime import date, timedelta

import pytest
from errors import (
    BookNotFoundError,
    BookNotOnLoanError,
    BookUnavailableError,
    DuplicateBookError,
    DuplicateMemberError,
    LoanLimitExceededError,
    MemberNotFoundError,
    UnpaidFeeError,
)
from library import Library
from models import REGULAR, STUDENT, Book, Member

TODAY = date(2026, 10, 1)


@pytest.fixture
def library(regular_member, student_member) -> Library:
    lib = Library()
    for i in range(1, 7):
        lib.add_book(Book(f"b{i}", f"本{i}"))
    lib.add_member(regular_member)  # m1: 一般
    lib.add_member(student_member)  # m2: 学生
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


def test_loansは読み取り専用のtuple(library):
    library.borrow("m1", "b1", TODAY)
    assert isinstance(library.loans, tuple)
