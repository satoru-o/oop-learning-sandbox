from dataclasses import FrozenInstanceError, replace

import pytest
from state import LibraryState


def test_初期状態はすべて空():
    state = LibraryState()
    assert (state.books, state.members, state.loans, state.reservations) == ((), (), (), ())


def test_変更できず_replaceで新しい状態を作る(book):
    state = LibraryState()
    with pytest.raises(FrozenInstanceError):
        state.books = (book,)

    updated = replace(state, books=(book,))
    assert updated.books == (book,)
    assert state.books == ()  # 元の状態は変わらない
