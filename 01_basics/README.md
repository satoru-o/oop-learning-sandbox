# 01_basics: 銀行口座と取引履歴（単一責任の原則 & コンポジション）

## 🎯 この章で学ぶこと
- **カプセル化**: 不正な値の書き換えを防ぐ状態の隠蔽とドメイン保護
- **単一責任の原則 (SRP)**: UI/ログ出力（I/O）とビジネスロジックの分離
- **コンポジション（Composition）**: クラスの中に別のクラスを持たせる設計
- **カスタム例外**: エラー状態を戻り値（boolean）ではなく例外で表現する

---

## 🏗️ クラス設計 & 責務一覧

`BankAccount` にすべてを詰め込まず、役割ごとにクラスを分割します。

```text
[ 利用側 (main) ] --- 例外をキャッチ & ログ出力 (console / print)
        |
        v
[ BankAccount ] (口座の状態管理 & 取引検証)
        |
        +-- uses --> [ InsufficientBalanceError ] (残高不足例外)
        |
        +-- has  --> [ TransactionHistory ] (履歴の保持 & 参照)
                            |
                            +-- contains --> [ Transaction ] (1件の取引データ)

```

### 1. `Transaction` (値オブジェクト / Immutability)

1件の取引記録を表すイミュータブル（変更不可）なデータ構造。

* **プロパティ**:
* `id`: 取引ID (string / number)
* `type`: 種別 ("DEPOSIT" | "WITHDRAW")
* `amount`: 金額 (number)
* `timestamp`: 取引日時 (Date)



### 2. `TransactionHistory` (ファーストクラス・コレクション)

取引履歴の配列をカプセル化し、追加・参照ルールを管理する。

* **メソッド**:
* `add(type, amount)`: 記録を追加し `Transaction` を返す
* `get_all()` / `all`: 履歴一覧を取得（外部から直接 `push` できないようコピーや読み取り専用で返す）



### 3. `BankAccount` (ドメインエンティティ)

口座の残高計算とビジネスルール検証に特化。**`print` や `console.log` は一切行わない**。

* **プロパティ**:
* `owner`: 名義人 (readonly)
* `balance`: 残高 (readonly ゲッター)
* `history`: `TransactionHistory` のインスタンス


* **メソッド**:
* `deposit(amount)`: 1円以上の検証 -> 残高加算 -> 履歴記録 -> 新残高を返す（失敗時は Error）
* `withdraw(amount)`: 残高不足・1円未満の検証 -> 残高減算 -> 履歴記録 -> 新残高を返す（失敗時は `InsufficientBalanceError`）



---

## 🔍 実装時のポイント

* **I/Oの完全排除**: クラス内部では `print` や `console.log` を使わず、例外を `throw` する。
* **防御的コピー**: `history.get_all()` で配列を返す際、外部から `array.push()` で直接書き換えられない配慮をする。

