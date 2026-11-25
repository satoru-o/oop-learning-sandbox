---
id: "0001"
title: 値オブジェクトの中身は value で取り出す
status: accepted
date: 2026-11-25
layer: domain
decision: 値を1つだけ包む値オブジェクト（Url など）は、包んだ中身を属性 value で公開する
related:
  - src/shortener/domain.py
  - tests/test_domain_ca.py
supersedes:
superseded_by:
---

# 0001 値オブジェクトの中身は `value` で取り出す

## 背景

最初のテストで `Url("https://example.com").value` と書いた。
`value` は抽象的な名前なので、もっと具体的な名前にすべきかを検討した。

## 決定

値を1つだけ包む値オブジェクトは、中身を属性 `value` で公開する。

- `url.value` は「URL の値」と読める。何の値かはクラス名 `Url` が表している
- このあと作る `Code` なども同じ形にそろえ、「包んだ中身は `.value` で取り出す」という決まり1つで済ませる
- 項目が2つ以上あるクラス（例: 06・09章の `Room.name`、`User.position`）は、項目を区別するために具体的な名前を付ける。この決定の対象外

## 検討した他の案

| 案 | 採らなかった理由 |
| --- | --- |
| `url.url` | 同じ語の繰り返しになる |
| `url.text` / `url.raw` | `value` と抽象度が変わらず、決まりとしてそろえにくい |
| `str(url)`（`__str__`） | `__str__` は人に見せる表示用。保存のための変換にも使うと役割が混ざる |

## 結果

- 中身を取り出すのは主に外側（保存・表示）で、そこでは `.value` を読めばよい
- `value` をメソッドではなく属性にしたので、カッコなしで読める
