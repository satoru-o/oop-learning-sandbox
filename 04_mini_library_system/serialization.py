# 04_mini_library_system/serialization.py
# LibraryState と dict（JSON にできる形）の相互変換。純粋関数でファイルは触らない。
from datetime import date

from errors import CorruptedDataError
from models import POLICIES, Book, Loan, Member, Reservation
from state import LibraryState

SCHEMA_VERSION = 1


def state_to_dict(state: LibraryState) -> dict:
    return {
        "version": SCHEMA_VERSION,
        "books": [{"book_id": b.book_id, "title": b.title} for b in state.books],
        "members": [
            {"member_id": m.member_id, "name": m.name, "policy": m.policy.name}
            for m in state.members
        ],
        "loans": [
            {
                "member_id": loan.member.member_id,
                "book_id": loan.book.book_id,
                "borrowed_on": loan.borrowed_on.isoformat(),
                "due_on": loan.due_on.isoformat(),
                "returned_on": _iso(loan.returned_on),
                "late_fee": loan.late_fee,
                "fee_paid": loan.fee_paid,
            }
            for loan in state.loans
        ],
        "reservations": [
            {
                "member_id": r.member.member_id,
                "book_id": r.book.book_id,
                "reserved_on": r.reserved_on.isoformat(),
                "hold_until": _iso(r.hold_until),
            }
            for r in state.reservations
        ],
    }


def state_from_dict(data: object) -> LibraryState:
    """dict から LibraryState を復元する。不正なデータは CorruptedDataError"""
    version = _field(data, "version", int)
    if version != SCHEMA_VERSION:
        raise CorruptedDataError(f"未対応のバージョンです: {version}")

    books = _unique(
        (Book(_field(b, "book_id", str), _field(b, "title", str)) for b in _items(data, "books")),
        key=lambda b: b.book_id,
        label="本",
    )
    members = _unique(
        (_member(m) for m in _items(data, "members")), key=lambda m: m.member_id, label="会員"
    )
    book_by_id = {b.book_id: b for b in books}
    member_by_id = {m.member_id: m for m in members}

    loans = tuple(
        Loan(
            member=_lookup(member_by_id, _field(item, "member_id", str), "会員"),
            book=_lookup(book_by_id, _field(item, "book_id", str), "本"),
            borrowed_on=_date(item, "borrowed_on"),
            due_on=_date(item, "due_on"),
            returned_on=_optional_date(item, "returned_on"),
            late_fee=_field(item, "late_fee", int),
            fee_paid=_field(item, "fee_paid", bool),
        )
        for item in _items(data, "loans")
    )
    reservations = tuple(
        Reservation(
            member=_lookup(member_by_id, _field(item, "member_id", str), "会員"),
            book=_lookup(book_by_id, _field(item, "book_id", str), "本"),
            reserved_on=_date(item, "reserved_on"),
            hold_until=_optional_date(item, "hold_until"),
        )
        for item in _items(data, "reservations")
    )
    return LibraryState(books, members, loans, reservations)


def _iso(value: date | None) -> str | None:
    return None if value is None else value.isoformat()


def _member(item: object) -> Member:
    policy_name = _field(item, "policy", str)
    if policy_name not in POLICIES:
        raise CorruptedDataError(f"未知の会員種別です: {policy_name}")
    return Member(_field(item, "member_id", str), _field(item, "name", str), POLICIES[policy_name])


def _field(item: object, key: str, expected: type):
    """dict から項目を取り出し、型を検証する（bool は int として扱わない）"""
    if not isinstance(item, dict):
        raise CorruptedDataError(f"オブジェクトではありません: {item!r}")
    if key not in item:
        raise CorruptedDataError(f"項目がありません: {key}")
    value = item[key]
    is_int_like_bool = expected is int and isinstance(value, bool)
    if not isinstance(value, expected) or is_int_like_bool:
        raise CorruptedDataError(f"項目 {key} の型が不正です: {value!r}")
    return value


def _items(data: object, key: str) -> list:
    return _field(data, key, list)


def _date(item: object, key: str) -> date:
    text = _field(item, key, str)
    try:
        return date.fromisoformat(text)
    except ValueError as e:
        raise CorruptedDataError(f"項目 {key} が日付として不正です: {text!r}") from e


def _optional_date(item: object, key: str) -> date | None:
    if isinstance(item, dict) and item.get(key, "") is None:
        return None
    return _date(item, key)


def _lookup(by_id: dict, key: str, label: str):
    if key not in by_id:
        raise CorruptedDataError(f"存在しない{label}を参照しています: {key}")
    return by_id[key]


def _unique(items, key, label: str) -> tuple:
    result = tuple(items)
    ids = [key(i) for i in result]
    if len(ids) != len(set(ids)):
        raise CorruptedDataError(f"{label}のIDが重複しています")
    return result
