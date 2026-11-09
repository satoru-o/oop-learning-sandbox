# 09 設計メモ（いいとこどりとパイプライン）

## 設計前提
- **データは名詞、処理は動詞**で切る。データは `frozen dataclass`（メソッドなし）、処理は関数
- クラスで振る舞いを持たせるのは、差し替えたい所だけ（`ScheduleRepository` の `Protocol`）
- 失敗は2種類に分ける（06 の考え方を戻した）
  - **業務上の失敗**は普通に起こるので `Error`（`Enum`）を値で返す
  - **バグ**（不変条件を破る値を作ろうとした）は `InvariantViolation`（例外）
- 戻り値は `Schedule | Error`。`Result` 型は作らず、`isinstance(x, Error)` で分ける

## 1. ファイルの役割（5ファイル）

| ファイル | 中身 | 流儀の出どころ |
| --- | --- | --- |
| `domain.py` | 型・不変条件・`overlaps` / `has_overlap` / `make_schedule` / `is_available` | 07 の型と `__post_init__` |
| `pipeline.py` | ルール（`check_allowed` / `check_exists`）、`run`、`reserve` / `cancel` | 新規。07 の純粋関数 + パイプライン |
| `codec.py` | `Schedule` ⇄ 辞書。外から来たデータを**型に変換**する | 08 の境界の考え方 |
| `storage.py` | `ScheduleRepository`（Protocol）とインメモリ実装（JSON で預かる） | 06・07 のリポジトリ |
| `shell.py` | `update_room`：読む → `reserve` / `cancel` → 書く | 07 の殻 |

## 2. パイプライン
`reserve` は「ルールを順に通して、全部通ったら適用する」だけ。

```python
RESERVE_RULES = (check_allowed,)   # 要求が増えたら、関数を書いてここに足す
CANCEL_RULES = (check_exists,)

def run(rules, apply, schedule, booking):
    for rule in rules:
        if (error := rule(schedule, booking)) is not None:
            return error
    return apply(schedule, booking)
```

- ルールは `(Schedule, Booking) -> Error | None`。形がそろっているのでテストも1行
- `reserve` と `cancel` が同じ `run` を使う（骨組みが1つ）
- 予約の依頼もキャンセルの依頼も `Booking` という同じ型で表せるので、専用の「リクエスト型」は作っていない
- 「重ならない」はルールにせず、適用（`add_booking`）が通る `make_schedule` に任せた

## 3. 4つの章の対比

| 観点 | 06 契約 | 07 関数型 | 08 データ指向 | 09 いいとこどり |
| --- | --- | --- | --- | --- |
| src のファイル数 | 8 | 8 | 6 | 5 |
| src のコード行（空行・コメント・説明書き除く） | 107 | 151 | 115 | 144 |
| src のコード文字数（同上） | 3,235 | 4,199 | 3,968 | 4,907 |
| 重なり判定のロジック | `_no_overlap`（1か所） | `__post_init__` と `is_available` で `overlaps` を呼ぶ | `validate` と `slots` | `has_overlap`（1か所） |
| 不変条件の守り方 | 全メソッドの前後 | 作る瞬間 | 境界で検証 | 作る瞬間（`__post_init__`）+ 業務の入口（`make_schedule`） |
| 失敗の表し方 | 例外（バグのみ） | `Ok` / `Err` | `{"ok": False, ...}` | `Error`（業務）と例外（バグ） |
| 要求の追加 | クラスを触る | 関数を触る | 関数を触る | ルールを足すだけ |
| 事後条件 | `icontract` | テスト | テスト | `hypothesis` の性質テスト |
| 外部依存 | icontract | なし | jsonschema | hypothesis（テストのみ） |

## 4. 契約を性質テストに置き換えた
06 の事後条件（件数+1 など）は、`icontract` ではなく `hypothesis` で確かめた（`tests/test_properties_pl.py`）。

- **ステートフルテスト**: 予約とキャンセルをランダムに繰り返し、毎回「予約同士は重ならない」「辞書にして戻しても同じ」を検査する
- 重なりの検査は、実装の `has_overlap` を使わず**別の書き方**（ブルートフォース）で行う。同じ関数で確かめると、バグまで一緒に見逃すため
- **変異を入れて確かめた**: 重なり判定を `a.start < b.start < a.end`（左右を入れ替えると結果が変わる）に壊すと、個別の例のテストは全部通ったが、ステートフルテストだけが落ちた。例では思いつかなかった入力を、性質テストが見つけた
- 契約は1回の呼び出ししか見ないが、性質テストは操作の**列**を見る

## 5. 簡素になったと言えること・言えないこと

### 言えること
- ファイル数が減り、概念が減った（`ExecutiveRoom`・`Anyone`/`MinPosition`・`Result`・`Access` がない）
- 重なり判定のロジックが1か所
- 要求を足す場所が決まっている（ルールの関数 + タプル）
- 保存は `codec` と `storage` に閉じていて、ドメインは JSON を知らない

### 言えないこと
- **コードの量は減っていない**。コード行は 06（107）や 08（115）より多く、07（151）とほぼ同じ。文字数（4,907）は4章の中で最大で、型注釈や `Rule` の型定義が増えた分が効いている。減ったのは「ファイル数」と「概念の数」
- 行数の数え方で結論が変わらないよう、説明書き（docstring）とコメントは除いて数えた（`ast` と `tokenize` で判定）。生の行数や文字数で比べると、説明書きを多く付けた章ほど大きく見える（09 は生の文字数の約25%が説明書き、06 は約17%）
- 検査点は「1か所」ではなく、判定ロジックが1か所で、**守る入口は2つ**（`Schedule` 自身の `__post_init__` と `make_schedule`）。前者はバグ用、後者は業務用
- Python は型で不正な値を作れなくすることが弱く、`__post_init__` という実行時の検査に頼っている

## 6. 今回やらなかったこと
- `pydantic` による型・スキーマ・変換の一本化。`codec.py` の手書きの変換が二重定義になる点は残っている（`Schedule` の形を `dataclass` と `codec` の両方で知っている）
- ルールの設定付きの形（営業時間など）。必要になったら「ルールを作る関数」で包む（関数のままで足りる）
