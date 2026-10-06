import json
from copy import deepcopy

import pytest
from errors import CorruptedDataError, LibraryError, StorageError
from serialization import state_from_dict, state_to_dict
from state import LibraryState


def test_保存して読み込むと元の状態に戻る(full_state):
    assert state_from_dict(state_to_dict(full_state)) == full_state


def test_空の状態も往復できる():
    assert state_from_dict(state_to_dict(LibraryState())) == LibraryState()


def test_出力はJSONにできる形で_日付はISO形式_会員種別は名前(full_state):
    data = json.loads(json.dumps(state_to_dict(full_state)))

    assert data["version"] == 1
    assert data["members"][1] == {"member_id": "m2", "name": "学生花子", "policy": "学生"}
    assert data["loans"][0] == {
        "member_id": "m1",
        "book_id": "b1",
        "borrowed_on": "2026-10-01",
        "due_on": "2026-10-15",
        "returned_on": None,
        "late_fee": 0,
        "fee_paid": False,
    }
    assert data["reservations"][0]["hold_until"] is None
    assert data["reservations"][1]["hold_until"] == "2026-10-27"


def test_JSONを経由しても元に戻る(full_state):
    restored = state_from_dict(json.loads(json.dumps(state_to_dict(full_state))))
    assert restored == full_state


def test_StorageErrorは業務例外とは別系統():
    assert not issubclass(StorageError, LibraryError)
    assert issubclass(CorruptedDataError, StorageError)


def _broken(mutate):
    def make(state: LibraryState) -> dict:
        data = deepcopy(state_to_dict(state))
        mutate(data)  # 戻り値（pop の結果など）は使わず、変更後の data を返す
        return data

    return make


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda d: d.pop("version"), id="versionがない"),
        pytest.param(lambda d: d.update(version=999), id="未対応のversion"),
        pytest.param(lambda d: d.pop("books"), id="booksがない"),
        pytest.param(lambda d: d.update(books="not a list"), id="booksがリストでない"),
        pytest.param(lambda d: d["books"][0].pop("title"), id="本の項目が欠けている"),
        pytest.param(lambda d: d["books"][0].update(title=123), id="本の型が違う"),
        pytest.param(lambda d: d["books"].append(dict(d["books"][0])), id="本のIDが重複"),
        pytest.param(lambda d: d["members"].append(dict(d["members"][0])), id="会員のIDが重複"),
        pytest.param(lambda d: d["members"][0].update(policy="教職員"), id="未知の会員種別"),
        pytest.param(lambda d: d["loans"][0].update(member_id="m999"), id="貸出の会員が存在しない"),
        pytest.param(lambda d: d["loans"][0].update(book_id="b999"), id="貸出の本が存在しない"),
        pytest.param(lambda d: d["loans"][0].update(due_on="2026/10/15"), id="日付の形式が違う"),
        pytest.param(lambda d: d["loans"][0].update(late_fee="50"), id="延滞料が数値でない"),
        pytest.param(lambda d: d["loans"][0].update(late_fee=True), id="延滞料が真偽値"),
        pytest.param(lambda d: d["loans"][0].update(fee_paid="yes"), id="支払済みが真偽値でない"),
        pytest.param(
            lambda d: d["reservations"][0].update(member_id="m999"), id="予約の会員が存在しない"
        ),
        pytest.param(
            lambda d: d["reservations"][0].update(book_id="b999"), id="予約の本が存在しない"
        ),
        pytest.param(
            lambda d: d["reservations"][1].update(hold_until=20261027), id="期限の型が違う"
        ),
    ],
)
def test_壊れたデータはCorruptedDataErrorになる(full_state, mutate):
    with pytest.raises(CorruptedDataError):
        state_from_dict(_broken(mutate)(full_state))


@pytest.mark.parametrize("data", [None, [], "text", 123])
def test_辞書でないデータはCorruptedDataError(data):
    with pytest.raises(CorruptedDataError):
        state_from_dict(data)
