from datetime import date, timedelta

import pytest
from errors import BookUnavailableError, CorruptedDataError, StorageError
from library import Library
from models import REGULAR, STUDENT, Book, Member
from repository import InMemoryRepository, JsonFileRepository
from state import LibraryState

TODAY = date(2026, 10, 1)


def day(n: int) -> date:
    return TODAY + timedelta(days=n)


class SpyRepository(InMemoryRepository):
    """保存回数を数え、失敗させることもできるテスト用の Repository"""

    def __init__(self):
        super().__init__()
        self.save_count = 0
        self.fail = False

    def save(self, state: LibraryState) -> None:
        if self.fail:
            raise StorageError("disk full")
        super().save(state)
        self.save_count += 1


@pytest.fixture
def repo() -> SpyRepository:
    return SpyRepository()


@pytest.fixture
def library(repo) -> Library:
    """m1 が b1 を借り、m2 が予約し、m3 は延滞料50円が未払いの状態"""
    lib = Library(repo)
    for i in range(1, 5):
        lib.add_book(Book(f"b{i}", f"本{i}"))
    lib.add_member(Member("m1", "一般太郎", REGULAR))
    lib.add_member(Member("m2", "学生花子", STUDENT))
    lib.add_member(Member("m3", "一般三郎", REGULAR))

    lib.borrow("m1", "b1", TODAY)
    lib.reserve("m2", "b1", TODAY)
    lib.borrow("m3", "b2", TODAY)
    lib.return_book("b2", day(19))  # 5日延滞 = 50円
    return lib


# 変更系のすべての操作
OPERATIONS = {
    "add_book": lambda lib: lib.add_book(Book("b9", "新刊")),
    "add_member": lambda lib: lib.add_member(Member("m9", "新会員", REGULAR)),
    "borrow": lambda lib: lib.borrow("m1", "b3", day(20)),
    "return_book": lambda lib: lib.return_book("b1", day(20)),
    "pay_fee": lambda lib: lib.pay_fee("m3"),
    "reserve": lambda lib: lib.reserve("m3", "b1", day(20)),
    "cancel_reservation": lambda lib: lib.cancel_reservation("m2", "b1", day(20)),
}


def test_デフォルトはメモリ上で動く():
    library = Library()
    library.add_book(Book("b1", "本1"))
    assert library.state.books == (Book("b1", "本1"),)


def test_起動時にRepositoryから状態を読み込む(full_state):
    library = Library(InMemoryRepository(full_state))
    assert library.state == full_state
    assert library.loans == full_state.loans
    assert library.reservations == full_state.reservations


@pytest.mark.parametrize("name", OPERATIONS)
def test_変更系の操作は成功すると保存される(library, repo, name):
    before = repo.save_count
    OPERATIONS[name](library)

    assert repo.save_count == before + 1
    assert repo.load() == library.state  # 保存された内容とメモリの状態が一致


@pytest.mark.parametrize("name", OPERATIONS)
def test_保存に失敗したら状態は変わらずStorageError(library, repo, name):
    before = library.state
    repo.fail = True

    with pytest.raises(StorageError):
        OPERATIONS[name](library)

    assert library.state == before
    assert repo.load() == before


def test_保存に失敗しても_直後に再試行すれば成功する(library, repo):
    repo.fail = True
    with pytest.raises(StorageError):
        library.borrow("m1", "b3", day(20))

    repo.fail = False
    loan = library.borrow("m1", "b3", day(20))
    assert loan in library.loans


def test_業務ルール違反の操作は保存も変更もしない(library, repo):
    before, saves = library.state, repo.save_count

    with pytest.raises(BookUnavailableError):
        library.borrow("m2", "b1", day(20))  # b1 は貸出中

    assert library.state == before
    assert repo.save_count == saves


def test_支払うものがなければ保存しない(library, repo):
    saves = repo.save_count
    assert library.pay_fee("m1") == 0
    assert repo.save_count == saves


def test_ファイルに保存して別のLibraryで続きから使える(tmp_path):
    path = tmp_path / "library.json"

    first = Library(JsonFileRepository(path))
    first.add_book(Book("b1", "本1"))
    first.add_member(Member("m1", "一般太郎", REGULAR))
    first.add_member(Member("m2", "学生花子", STUDENT))
    first.borrow("m1", "b1", TODAY)
    first.reserve("m2", "b1", TODAY)

    second = Library(JsonFileRepository(path))  # 再起動したつもり
    assert second.state == first.state
    assert second.reservations[0].member.member_id == "m2"

    second.return_book("b1", day(3))
    loan = second.borrow("m2", "b1", day(4))  # 予約も引き継がれている
    assert loan.member.member_id == "m2"

    third = Library(JsonFileRepository(path))
    assert third.state == second.state
    assert third.reservations == ()


def test_壊れたファイルでは起動できない(tmp_path):
    path = tmp_path / "library.json"
    path.write_text("{ broken", encoding="utf-8")
    with pytest.raises(CorruptedDataError):
        Library(JsonFileRepository(path))
