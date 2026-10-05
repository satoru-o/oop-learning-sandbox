# 03_design_patterns: 価格計算エンジン（Strategy パターン）

## 🎯 この章で学ぶこと
- **Strategy パターン**: アルゴリズム（計算ロジック）をクラスとしてカプセル化し、実行時に動的に切り替える
- **Open-Closed Principle (OCP)**: 既存のコード（Cart）を変更せずに、新しい割引ルール（Strategy）を追加できるようにする
- **コンポジション vs 継承**: 継承でクラスを増やしまくるのではなく、戦略オブジェクトを注入（DI）して挙動を変える

---

## 💡 なぜ Strategy パターンが必要か？

もし `Cart` クラスの中で `if (user.isVip) { ... } else if (isBlackFriday) { ... }` のように条件分岐を書いていると、新しいキャンペーンが増えるたびに `Cart` クラスが巨大化して破壊されます。

割引ロジックを「戦略（Strategy）」として独立させ、`Cart` に持たせる（セットする）ことで解決します。

---

## 🏗️ クラス設計 & 責務一覧

```text
               [ DiscountStrategy ] (抽象戦略)
               /        |         \
              /         |          \
   [ FixedDiscount ] [ PercentageDiscount ] [ BulkDiscount ]
              \         |          /
               v        v         v
           [ ShoppingCart ] (戦略を保持して計算を委譲)

```

### 1. `DiscountStrategy` (抽象戦略)

すべての割引ルールのインターフェース / 抽象クラス。

* **抽象メソッド**:
* `apply_discount(original_price: float) -> float`: 元の価格を受け取り、割引後の価格を返す



### 2. 具象戦略クラス群 (Concrete Strategies)

* **`RegularPricing`**: 割引なし（定価通り）
* **`FixedDiscount`**: 定額引き（例: 500円引き）
* **`PercentageDiscount`**: 定率引き（例: 20% OFF）
* **`BulkDiscount`**: まとめ買い割引（例: 3個以上購入で20% OFF）

### 3. `ShoppingCart` (コンテキスト)

カートの中身（合計金額）の管理と、セットされた `DiscountStrategy` を使った最終価格の計算を担当。

* **プロパティ**:
* `items`: 商品リスト
* `discount_strategy`: 適用中の `DiscountStrategy`


* **メソッド**:
* `set_discount_strategy(strategy)`: 割引戦略を動的に変更
* `calculate_total()`: 戦略を使って割引後の合計金額を計算
