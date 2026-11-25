---
id: "0002"
title: 値オブジェクトは frozen dataclass で作る
status: accepted
date: 2026-11-25
layer: domain
decision: 値オブジェクトは @dataclass(frozen=True) で作り、検査は __post_init__ に書いて、違反したら例外を投げる
related:
  - src/shortener/domain.py
  - tests/test_domain_ca.py
  - notes/frozen-dataclass.md
  - "0001"
supersedes:
superseded_by:
---

# 0002 値オブジェクトは frozen dataclass で作る

## 背景

`Url` を普通のクラスで作り、`__init__` で http/https とホスト名を検査していた。
ところが、作ったあとに `url.value = "ftp://..."` と代入でき、検査をすり抜けられた。
また、中身が同じ `Url` 同士でも `==` が `False` になった。
要求3（同じURLは同じコード）を作るときに、「同じURL」を判定できない。

## 決定

値オブジェクトは `@dataclass(frozen=True)` で作る。

- 作ったあとに書き換えられないので、`__post_init__` を通った正しい値だけが存在し続ける
- `==` は中身で比べ、`__hash__` も中身から作られるので、`dict` のキーにできる
- 検査は `__post_init__` に書き、違反したら domain の例外（例: `InvalidUrlError`）を投げる
- テストでは、書き換えられないことを `FrozenInstanceError` ではなく `AttributeError` で確かめる。作り方ではなく振る舞いを確かめるため

## 検討した他の案

| 案 | 採らなかった理由 |
| --- | --- |
| 普通のクラス + `__eq__`・`__hash__` を手で書く | dataclass が自動で作るものを手で書くことになる。代入の禁止も自分で書く必要がある |
| `typing.NamedTuple` | タプルなので `Url("a") == ("a",)` が `True` になり、別の型と区別できない |
| `str` を継承する | `str` のメソッド（`replace` など）が全部使え、戻り値はただの `str` になる。検査を通っていない値が混ざりやすい |

## 結果

- `Url` は代入できず、中身で比べられるようになった（テスト「作ったあと書き換えられない」「同じURLのUrlは等しい」）
- このあと作る `Code` なども同じ形にそろえる
- 値を整える（例: 前後の空白を削る）必要が出たら、`__post_init__` の中で `object.__setattr__` を使う
