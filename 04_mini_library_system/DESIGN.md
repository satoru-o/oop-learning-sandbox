# 04_mini_library_system: 設計図

図書館の貸出管理システムの設計メモです。図は [Mermaid](https://mermaid.js.org/) で書いています（VS Code の Markdown プレビュー / GitHub で描画できます）。

**設計の前提**
- 会員種別の違いは数値だけなので、継承せず `MembershipPolicy` を `Member` に持たせる（コンポジション）
- 「貸出中か」は `Book` にフラグを持たず、`Loan` から導出する（二重管理しない）
- 延滞料と支払状況は `Loan` が持つ。会員の未払い額は、その会員の `Loan` の未払い分の合計で求める
- 延滞料は**返却時に確定**する（返却前の延滞中は料金が未確定）
- **純粋関数の核 + 状態を持つ殻**（functional core, imperative shell）
  - 期限計算・延滞料計算・貸出可否の判定は `rules.py` の純粋関数にする
  - `Book` / `Member` / `Loan` / `MembershipPolicy` はイミュータブル（`frozen=True`）。返却・支払いは新しい `Loan` を返す
  - 状態を変更するのは `Library` だけ

### どこが純粋で、どこが状態を持つか

| 層 | 要素 | 性質 |
| --- | --- | --- |
| 核（純粋） | `rules.py` の関数群 | 引数だけで結果が決まる。副作用なし。日付も引数で受ける |
| 核（値） | `Book` / `Member` / `Loan` / `MembershipPolicy` | イミュータブルな値オブジェクト |
| 殻（状態） | `Library` | 蔵書・会員・貸出記録を保持し、核を呼んで結果を反映する |

---

## 1. コンテキスト図

システムの境界と、外との関わりを示します。このシステムの範囲は「ドメインモデル」だけで、UI・DB・決済は含みません。

```mermaid
flowchart LR
    user(["👤 会員（一般ユーザー）<br/>（デモコードが代役）"])

    subgraph system["図書館貸出管理システム（04_mini_library_system）"]
        library["Library（殻）<br/>貸出・返却・延滞料支払いの窓口"]
        rules["rules.py（核）<br/>純粋関数: 期限・延滞料・貸出可否"]
        domain["値オブジェクト<br/>Book / Member / Loan / MembershipPolicy"]
        library --> rules
        library --> domain
        rules --> domain
    end

    clock["🕒 今日の日付<br/>（引数で外から渡す）"]
    ui["UI / Web"]:::out
    db["DB / 永続化"]:::out
    pay["決済サービス"]:::out

    user -- "borrow / return_book / pay_fee" --> library
    clock -. "today" .-> library
    library -. "例外 or 戻り値で結果を返す" .-> user
    ui ~~~ db ~~~ pay

    classDef out stroke-dasharray: 4 4,color:#888,stroke:#888;
```

> 点線の灰色ボックスは**スコープ外**です。「今日」を引数で受けるのは、延滞のテストを書きやすくする（時刻という副作用を持ち込まない）ためです。

---

## 2. 状態遷移図

### 2-1. `Loan`（貸出）の状態

`Loan` はイミュータブルなので、遷移のたびに**新しい `Loan` 値**が作られます（`dataclasses.replace`）。

```mermaid
stateDiagram-v2
    [*] --> 貸出中: borrow（期限 = 貸出日 + loan_days）

    貸出中 --> 完了: closed（延滞なし 延滞料 0円）
    貸出中 --> 延滞料未払い: closed（期限超過 延滞料 = 延滞日数 × 単価）

    延滞料未払い --> 完了: paid

    完了 --> [*]

    note right of 延滞料未払い
        この状態の Loan を持つ会員は
        新規に借りられない（ルール5）
    end note
```

### 2-2. `Book`（本）の状態（`Loan` から導出）

`Book` 自身は状態を持ちません。「返却日が未設定の `Loan` があるか」で決まります。

```mermaid
stateDiagram-v2
    [*] --> 貸出可能
    貸出可能 --> 貸出中: Loan が作られる
    貸出中 --> 貸出可能: Loan が返却される
```

---

## 3. クラス図

```mermaid
classDiagram
    direction LR

    class MembershipPolicy {
        <<frozen dataclass>>
        +str name
        +int max_loans
        +int loan_days
        +int late_fee_per_day
    }

    class Book {
        <<frozen dataclass>>
        +str book_id
        +str title
    }

    class Member {
        <<frozen dataclass>>
        +str member_id
        +str name
        +MembershipPolicy policy
    }

    class Loan {
        <<frozen dataclass>>
        +Member member
        +Book book
        +date borrowed_on
        +date due_on
        +date returned_on
        +int late_fee
        +bool fee_paid
        +is_active() bool
        +has_unpaid_fee() bool
        +closed(today, late_fee) Loan
        +paid() Loan
    }

    class rules {
        <<module / 純粋関数>>
        +calc_due_date(borrowed_on, policy) date
        +calc_late_fee(due_on, returned_on, policy) int
        +is_book_available(loans, book_id) bool
        +count_active_loans(loans, member_id) int
        +total_unpaid_fee(loans, member_id) int
        +check_can_borrow(policy, active_count, unpaid_fee, available) None
    }

    class Library {
        <<状態を持つ殻>>
        -dict books
        -dict members
        -list loans
        +add_book(book)
        +add_member(member)
        +borrow(member_id, book_id, today) Loan
        +return_book(book_id, today) Loan
        +pay_fee(member_id) int
        +loans tuple
    }

    class LibraryError {
        <<exception>>
    }
    class BookUnavailableError {
        <<exception>>
    }
    class LoanLimitExceededError {
        <<exception>>
    }
    class UnpaidFeeError {
        <<exception>>
    }
    class BookNotFoundError {
        <<exception>>
    }
    class MemberNotFoundError {
        <<exception>>
    }
    class BookNotOnLoanError {
        <<exception>>
    }
    class DuplicateBookError {
        <<exception>>
    }
    class DuplicateMemberError {
        <<exception>>
    }

    Member --> MembershipPolicy : has-a
    Loan --> Member : 借りた人
    Loan --> Book : 借りた本
    Library o-- Book : 蔵書
    Library o-- Member : 会員
    Library o-- Loan : 貸出記録
    Library ..> rules : 判定・計算を委譲
    rules ..> Loan : 読むだけ
    LibraryError <|-- BookUnavailableError
    LibraryError <|-- LoanLimitExceededError
    LibraryError <|-- UnpaidFeeError
    LibraryError <|-- BookNotFoundError
    LibraryError <|-- MemberNotFoundError
    LibraryError <|-- BookNotOnLoanError
    LibraryError <|-- DuplicateBookError
    LibraryError <|-- DuplicateMemberError
    rules ..> LibraryError : 不可なら送出
```

> - 会員種別は `REGULAR` / `STUDENT` という `MembershipPolicy` の**インスタンス**です。クラスを増やさずに種別を追加できます。
> - `rules` は状態を持たないので、クラスではなくモジュールの関数として書きます。

---

## 4. シーケンス図

### 4-1. 本を借りる（`borrow`）

ルール 1・2・5 の判定は純粋関数 `check_can_borrow` が行います。`Library` は材料を集めて渡し、結果を反映するだけです。

```mermaid
sequenceDiagram
    actor 会員
    participant Lib as Library（殻）
    participant R as rules（純粋関数）

    会員->>Lib: borrow(member_id, book_id, today)
    Lib->>Lib: 会員と本を取得
    Lib->>R: count_active_loans(loans, member_id)
    R-->>Lib: 貸出中の冊数
    Lib->>R: total_unpaid_fee(loans, member_id)
    R-->>Lib: 未払い延滞料
    Lib->>R: is_book_available(loans, book_id)
    R-->>Lib: 貸出可能か

    Lib->>R: check_can_borrow(policy, 冊数, 未払い額, 貸出可能か)
    alt 未払いの延滞料がある（ルール5）
        R-->>Lib: UnpaidFeeError
        Lib-->>会員: UnpaidFeeError
    else 本が貸出中（ルール1）
        R-->>Lib: BookUnavailableError
        Lib-->>会員: BookUnavailableError
    else 貸出冊数が上限に達している（ルール2）
        R-->>Lib: LoanLimitExceededError
        Lib-->>会員: LoanLimitExceededError
    else 貸出OK
        R-->>Lib: None
        Lib->>R: calc_due_date(today, policy)
        R-->>Lib: 期限（14日後 or 21日後）
        Lib->>Lib: Loan を生成して loans に追加
        Lib-->>会員: Loan
    end
```

### 4-2. 本を返して、延滞料を払う（`return_book` → `pay_fee`）

期限を過ぎて返却した場合の流れです（ルール 3・4・6）。`Loan` は更新せず、新しい値に**置き換えます**。

```mermaid
sequenceDiagram
    actor 会員
    participant Lib as Library（殻）
    participant R as rules（純粋関数）
    participant L as Loan（値）

    会員->>Lib: return_book(book_id, today)
    Lib->>Lib: 貸出中の Loan を探す
    Lib->>R: calc_late_fee(loan.due_on, today, policy)
    R-->>Lib: 延滞料（延滞日数 × 単価）
    Lib->>L: closed(today, late_fee)
    L-->>Lib: 新しい Loan（返却済み）
    Lib->>Lib: loans 内の古い Loan を新しい Loan に置き換え
    Lib-->>会員: Loan（本は貸出可能に戻る）

    Note over 会員,Lib: 延滞料があれば、支払うまでこの会員は借りられない

    会員->>Lib: pay_fee(member_id)
    Lib->>R: total_unpaid_fee(loans, member_id)
    R-->>Lib: 支払うべき合計額
    loop 未払いの各 Loan
        Lib->>L: paid()
        L-->>Lib: 新しい Loan（支払済み）
        Lib->>Lib: 置き換え
    end
    Lib-->>会員: 支払った合計額
```

---

## 5. 設計の決めごと（ADR 風メモ）

| 決めたこと | 理由 | 別案 |
| --- | --- | --- |
| 会員種別は `Member` を継承せず `MembershipPolicy` で表現 | 違いが数値だけで、振る舞いは同じ | 継承 / Strategy（計算ロジックが変わるなら昇格） |
| 貸出状態は `Loan` から導出 | `Book` のフラグとの二重管理を避ける | `Book.is_borrowed` フラグ |
| 延滞料は `Loan` が持つ（A案） | 履歴が残り、更新箇所が一つで済む | `Member.unpaid_balance`（B案） |
| 延滞料は返却時に確定 | 実装が単純。返却前は金額が未確定 | 日次で加算する |
| 判定順は 未払い → 貸出中 → 上限 | 会員側の問題を先に伝える | 任意（要検討） |
| ロジックは `rules.py` の純粋関数に切り出す | 入力だけで結果が決まり、モックなしでテストできる | 各クラスのメソッドに持たせる（OOP寄り） |
| 値オブジェクトはイミュータブル（`frozen=True`） | 状態変更を `Library` に閉じ込められる | ミュータブルな `Loan.close()` |
| 不可の判定は純粋関数から例外を送出 | Pythonらしく単純。同じ入力なら必ず同じ例外なので決定的 | `Result` 型や理由の戻り値で返す（より FP 寄り） |
