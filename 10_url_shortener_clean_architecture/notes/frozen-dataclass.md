---
title: frozen dataclass で値オブジェクトを作る
date: 2026-11-25
topic: python
summary: "@dataclass(frozen=True) は __init__・__eq__・__hash__・__repr__ を自動で作り、代入を禁止する。検査は __post_init__ に書く"
related:
  - src/shortener/domain.py
  - tests/test_domain_ca.py
---

# frozen dataclass で値オブジェクトを作る

## 何をしてくれるのか

`@dataclass(frozen=True)` を付けると、クラスに書いた**項目の宣言**（`value: str`）を見て、Python がメソッドを自動で作る。

```python
@dataclass(frozen=True)
class Url:
    value: str

    def __post_init__(self):
        parts = urlsplit(self.value)
        if parts.scheme not in ("http", "https") or not parts.netloc:
            raise InvalidUrlError(self.value)
```

上のコードは、だいたい次のコードを手で書いたのと同じ動きになる。

```python
class Url:
    def __init__(self, value):            # 項目の宣言から作られる
        object.__setattr__(self, "value", value)
        self.__post_init__()              # 値を入れたあとに呼ばれる

    def __post_init__(self):              # ← 自分で書くのはここだけ
        parts = urlsplit(self.value)
        if parts.scheme not in ("http", "https") or not parts.netloc:
            raise InvalidUrlError(self.value)

    def __setattr__(self, name, value):   # frozen=True で作られる
        raise FrozenInstanceError(f"cannot assign to field {name!r}")

    def __eq__(self, other):              # 中身で比べる
        return type(other) is Url and self.value == other.value

    def __hash__(self):                   # 中身からハッシュを作る
        return hash((self.value,))

    def __repr__(self):                   # 表示用
        return f"Url(value={self.value!r})"
```

自分で書くのは**項目の宣言**と**`__post_init__`の検査**だけで、残りは全部自動。

## 普通のクラスとの違い

| | 普通のクラス | frozen dataclass |
| --- | --- | --- |
| `__init__` | 自分で書く | 項目の宣言から自動 |
| 検査を書く場所 | `__init__` の中（引数を見る） | `__post_init__` の中（`self.value` を見る） |
| `url.value = ...` | できてしまう（検査をすり抜ける） | `FrozenInstanceError`（`AttributeError` の仲間） |
| `Url("a") == Url("a")` | `False`（同じ物かを比べる） | `True`（中身を比べる） |
| `dict` のキー・`set` の要素 | 物ごとに別扱い | 中身が同じなら同じキー |
| `print(url)` | `<Url object at 0x...>` | `Url(value='https://...')` |

## 値オブジェクトに向いている理由

- **作ったあと書き換えられない**: `__post_init__` を通った正しい値だけが存在し続ける
- **中身で比べられる**: 「同じURL」を `==` で判定できる。要求3（同じURLは同じコード）で使う
- **`dict` のキーにできる**: 「URL → コード」の対応表を `dict` で持てる

## つまずきどころ

- `__post_init__` の中では、引数名ではなく `self.value` を見る
- `__post_init__` の中でも代入はできない。値を整える（例: 前後の空白を削る）必要があるときは `object.__setattr__(self, "value", ...)` を使う
- 凍るのは項目そのものだけ。項目が `list` などの場合、中身は書き換えられてしまう（`tuple` を使う）
