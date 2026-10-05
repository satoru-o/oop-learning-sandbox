from abc import ABC, abstractmethod
from dataclasses import dataclass


# カート内の商品アイテム
@dataclass(frozen=True)
class CartItem:
    name: str
    price: float
    quantity: int

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity


# 割引戦略の中小インターフェース
class DiscountStrategy(ABC):
    """すべての割引計算アルゴリズムの親クラス"""

    @abstractmethod
    def apply_discount(self, items: list[CartItem]) -> float:
        """商品リストを受け取り、割引適用後の最終合計金額を返す"""


# 具象戦略クラス群
class RegularPricing(DiscountStrategy):
    """通常料金"""

    def apply_discount(self, items):
        return sum(item.subtotal for item in items)


class FixedDiscount(DiscountStrategy):
    """定額引き戦略"""

    def __init__(self, discount_amount: float):
        if discount_amount < 0:
            raise ValueError("割引額は0以上を指定してください")
        self._discount_amount = discount_amount

    def apply_discount(self, items) -> float:
        subtotal = sum(item.subtotal for item in items)
        # 割引後の価格が0円未満にならないように保護
        return max(0.0, subtotal - self._discount_amount)


class PercentageDiscount(DiscountStrategy):
    """定率引き戦略"""

    def __init__(self, percent: float):
        if not (0 <= percent <= 100):
            raise ValueError("割引率は 0~100 の間で指定してください")
        self._percent = percent

    def apply_discount(self, items: list[CartItem]) -> float:
        subtotal = sum(item.subtotal for item in items)
        discount_factor = 1.0 - (self._percent / 100.0)
        return subtotal * discount_factor


class BulkDiscount(DiscountStrategy):
    """まとめ買い割引戦略"""

    def __init__(self, min_quantity: int, percent: float):
        if not (min_quantity > 0):
            raise ValueError("まとめ買い割引適用最小購買数は0個より大きい必要があります")
        if not (0 <= percent <= 100):
            raise ValueError("割引率は 0~100 の間で指定してください")

        self._min_quantity = min_quantity
        self._percent = percent

    def apply_discount(self, items: list[CartItem]) -> float:
        subtotal = sum(item.subtotal for item in items)
        total_quantity = sum(item.quantity for item in items)

        # 指定個数以上買っていれば割引適用、そうでなければ定価
        if total_quantity >= self._min_quantity:
            discount_factor = 1.0 - (self._percent / 100.0)
            return subtotal * discount_factor
        return subtotal


# ショッピングカート
class ShoppingCart:
    """
    カートクラス
    具体的にどう計算されるか知らず、DisCountStrategy に計算を全面的に委譲する
    """

    def __init__(self, strategy: DiscountStrategy | None = None):
        self._items: list[CartItem] = []
        # デフォルトは割引なし戦略
        self._strategy: DiscountStrategy = strategy or RegularPricing()

    def add_item(self, item: CartItem) -> None:
        self._items.append(item)

    def set_strategy(self, strategy: DiscountStrategy) -> None:
        """実行時に動的に割引ルールを切り替える"""
        self._strategy = strategy

    @property
    def raw_total(self) -> float:
        """割引適用前の小計"""
        return sum(item.subtotal for item in self._items)

    def calculate_total(self) -> float:
        """現在の戦略を使って最終合計金額を計算"""
        return self._strategy.apply_discount(self._items)


# =====================================================================
# 動作確認 (利用側)
# =====================================================================
if __name__ == "__main__":
    # カートの準備と商品の追加
    cart = ShoppingCart()
    cart.add_item(CartItem(name="Python入門書", price=3000, quantity=2))
    cart.add_item(CartItem(name="キーボード", price=8000, quantity=1))
    cart.add_item(CartItem(name="マウスパッド", price=1000, quantity=2))

    print(f"--- 定価小計: {cart.raw_total:,.0f}円 ---")

    # 1. 通常料金（デフォルト）
    print(f"通常時（割引なし）: {cart.calculate_total():,.0f}円")

    # 2. クーポン適用（1,000円引き）
    cart.set_strategy(FixedDiscount(1000))
    print(f"1,000円引きクーポン適用: {cart.calculate_total():,.0f}円")

    # 3. ブラックフライデーセール（20% OFF）
    cart.set_strategy(PercentageDiscount(20))
    print(f"ブラックフライデー (20% OFF): {cart.calculate_total():,.0f}円")

    # 4. まとめ買いキャンペーン（5個以上で15% OFF）
    # 現在の合計個数は 2 + 1 + 2 = 5個 なので条件達成！
    cart.set_strategy(BulkDiscount(min_quantity=5, percent=15))
    print(f"まとめ買い割引 (5個以上で15% OFF): {cart.calculate_total():,.0f}円")
