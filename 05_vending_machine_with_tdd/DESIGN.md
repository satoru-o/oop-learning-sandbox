# 05_vending_machine_with_tdd: 設計図

自動販売機の設計メモです。TDDで育てるので、**今コードにあるものだけ**を書き、増えたら更新します。図は [Mermaid](https://mermaid.js.org/) です（VS Code の Markdown プレビュー / GitHub で描画できます）。

**設計の前提**
- 責務ごとにクラスを分け、`VendingMachine` は部品に聞いて判断をまとめる窓口にする
- 状態を持つクラスは、フィールドを `private` にして getter 経由で読ませる。変わらない値は `readonly` で公開する
- `buy` は**全部のチェックを通してから状態を変える**。途中で失敗しても、在庫・残高・釣り銭箱は変わらない
- 支払い方法は `PaymentMethod`（インターフェース）にし、現金／ICカードを差し替えられる。`VendingMachine` は種類による分岐を持たない
- `print` はしない。結果は戻り値か例外で返す

---

## 1. クラス図（現状）

```mermaid
classDiagram
    VendingMachine o-- PaymentMethod : 持つ（差し替え可能）
    VendingMachine o-- "0..*" Slot : 持つ
    VendingMachine o-- CoinBox : 持つ
    VendingMachine o-- SalesLedger : 持つ
    Slot --> Product : 持つ
    PaymentMethod <|.. CashPayment
    PaymentMethod <|.. ICCardPayment

    class VendingMachine {
        +balance number
        +sales SalesLedger
        +insertMoney(money)
        +buy(productName) Record
        +refund() number
    }
    class Product {
        +name string
        +price number
    }
    class Slot {
        +product Product
        +stock number
        +hasStock boolean
        +dispense()
    }
    class PaymentMethod {
        <<interface>>
        +balance number
        +insert(money)
        +canPay(price) boolean
        +changeFor(price) number
        +pay(price) number
        +refund() number
    }
    class CashPayment {
        現金。釣り銭あり
    }
    class ICCardPayment {
        カード。釣り銭なし
    }
    class CoinBox {
        +count(value) number
        +payOut(amount) Record
    }
    class SalesLedger {
        +record(name, price)
        +countOf(name) number
        +amountOf(name) number
        +totalAmount number
    }
```

| クラス | 責務 | 持つ状態 |
| --- | --- | --- |
| `Product` | 商品の名前と価格 | 不変 |
| `Slot` | 1列ぶんの商品と在庫 | 在庫数 |
| `PaymentMethod` | 支払い方法の共通の約束（払えるか・釣り銭・支払い・払い戻し） | — |
| `CashPayment` | 現金。投入額の検証、釣り銭あり、払い戻しで残高を返す | 残高 |
| `ICCardPayment` | ICカード。釣り銭なし、カードの残高から引き落とし、現金は投入不可 | カード残高 |
| `CoinBox` | 釣り銭用の硬貨の枚数と、払い出しの組み合わせ | 額面ごとの枚数 |
| `SalesLedger` | 商品別の販売数・金額の集計 | 商品ごとの集計 |
| `VendingMachine` | 上の部品を束ねる窓口 | 部品への参照 |

---

## 2. 購入の流れ（`buy`）

```mermaid
sequenceDiagram
    actor 客
    participant VM as VendingMachine
    participant S as Slot
    participant P as PaymentMethod（現金）
    participant C as CoinBox

    客->>VM: insertMoney(500)
    VM->>P: insert(500)（10/50/100/500/1000以外は例外）
    客->>VM: buy("お茶")
    VM->>S: 商品を探す／hasStock は？
    S-->>VM: 在庫あり
    VM->>P: canPay(120) は？
    P-->>VM: 払える
    VM->>P: changeFor(120) は？
    P-->>VM: 380（ICカードなら 0）
    VM->>C: payOut(380)（払い出せなければ例外）
    C-->>VM: {100:3, 50:1, 10:3}
    Note over VM,C: ここまでに失敗したら何も変わらない
    VM->>P: pay(120) → refund()
    VM->>S: dispense()
    VM->>VM: sales.record("お茶", 120)
    VM-->>客: 釣り銭の硬貨
```

---

## 3. 実装済みのルール

| README | ルール | 担当 | テスト |
| --- | --- | --- | --- |
| 1 | 10/50/100/500/1000円のみ受け付ける | `CashPayment` | `存在しない金額(7円)は投入できないこと` |
| 2 | 商品は名前・価格・在庫を持つ | `Product` / `Slot` | `列は商品と在庫を持つこと` ほか |
| 3 | 買える（釣り銭を返す） | `VendingMachine.buy` | `購入すると釣り銭を返し、在庫と残高が減ること` |
| 4 | 残高不足・在庫切れは買えない | `PaymentMethod` / `Slot` | `残高が足りないと購入できず…` `在庫切れだと購入できず…` |
| 5 | 釣り銭切れは買えない | `CoinBox` | `釣り銭を払い出せないと購入できず…` |
| 6 | 払い戻しで残高が0に戻る | `CashPayment.refund` |
| 7 | 支払い方法を現金／ICカードで差し替えられる | `PaymentMethod` | `釣り銭箱が空でも購入でき、カードの残高から…`（`ic_card_payment.test.ts` ほか） |
| 8 | 売上（商品別の販売数・金額）を集計できる | `SalesLedger` | `商品別の販売数と金額を集計できること` | `払い戻しすると…` |

---

## 4. 残っていること

- 投入された硬貨は、いまは釣り銭箱に入らない（釣り銭箱は初期値のまま）
- 支払い方法は `VendingMachine` を作るときに決める（利用中に切り替える操作はない）
- エラーは `Error` のメッセージで区別している。専用の例外クラス（`OutOfStockError` など）にする余地がある
