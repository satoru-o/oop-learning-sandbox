// カート内の商品アイテム
export interface CartItem {
  readonly name: string;
  readonly price: number;
  readonly quantity: number;
}

/**
 * CartItem の小計を計算するヘルパー関数
 */
export function getSubtotal(item: CartItem): number {
  return item.price * item.quantity;
}

// 割引戦略のインターフェース
export interface DiscountStrategy {
  /**
   * 商品リストを受け取り、割引適用後の【最終合計金額】を返す
   */
  applyDiscount(items: ReadonlyArray<CartItem>): number;
}

// 具象戦略クラス群
export class RegularPricing implements DiscountStrategy {
  public applyDiscount(items: ReadonlyArray<CartItem>): number {
    return items.reduce((sum, item) => sum + getSubtotal(item), 0);
  }
}

export class FixedDiscount implements DiscountStrategy {
  constructor(private readonly discountAmount: number) {
    if (discountAmount < 0) {
      throw new Error("割引額は0以上を指定してください");
    }
  }

  public applyDiscount(items: ReadonlyArray<CartItem>): number {
    const subtotal = items.reduce((sum, item) => sum + getSubtotal(item), 0);
    return Math.max(0, subtotal - this.discountAmount);
  }
}

export class PercentageDiscount implements DiscountStrategy {
  constructor(private readonly percent: number) {
    if (percent < 0 || percent > 100) {
      throw new Error("割引率は 0~100 の間で指定してください");
    }
  }

  public applyDiscount(items: ReadonlyArray<CartItem>): number {
    const subtotal = items.reduce((sum, item) => sum + getSubtotal(item), 0);
    const discountFactor = 1.0 - this.percent / 100.0;
    return subtotal * discountFactor;
  }
}

export class BulkDiscount implements DiscountStrategy {
  constructor(
    private readonly minQuantity: number,
    private readonly percent: number
  ) {
    if (minQuantity < 0) {
      throw new Error("まとめ買い割引適用最小購買数は0個より大きい必要があります");
    }
    if (percent < 0 || percent > 100) {
      throw new Error("割引率は 0~100 の間で指定してください")
    }
  }

  public applyDiscount(items: ReadonlyArray<CartItem>): number {
    const subtotal = items.reduce((sum, item) => sum + getSubtotal(item), 0);
    const totalQuantity = items.reduce((sum, item) => sum + item.quantity, 0);

    if (totalQuantity >= this.minQuantity) {
      const discountFactor = 1.0 - this.percent / 100.0;
      return subtotal * discountFactor;
    }
    return subtotal;
  }
}

// --- 4. ショッピングカート (Context) ---
export class ShoppingCart {
  private readonly items: CartItem[] = [];
  private strategy: DiscountStrategy;

  constructor(strategy?: DiscountStrategy) {
    this.strategy = strategy ?? new RegularPricing();
  }

  public addItem(item: CartItem): void {
    this.items.push(item);
  }

  public setStrategy(strategy: DiscountStrategy): void {
    this.strategy = strategy;
  }

  get rawTotal(): number {
    return this.items.reduce((sum, item) => sum + getSubtotal(item), 0);
  }

  public calculateTotal(): number {
    return this.strategy.applyDiscount(this.items);
  }
}

// =====================================================================
// 動作確認 (利用側)
// =====================================================================
function main() {
  const cart = new ShoppingCart();
  cart.addItem({ name: "TypeScriptプログラミング", price: 3000, quantity: 2 });
  cart.addItem({ name: "キーボード", price: 8000, quantity: 1 });
  cart.addItem({ name: "マウスパッド", price: 1000, quantity: 2 });

  console.log(`--- 定価小計: ${cart.rawTotal.toLocaleString()}円 ---`);

  // 1. 通常料金（デフォルト）
  console.log(`通常時（割引なし）: ${cart.calculateTotal().toLocaleString()}円`);

  // 2. クーポン適用（1,000円引き）
  cart.setStrategy(new FixedDiscount(1000));
  console.log(`1,000円引きクーポン適用: ${cart.calculateTotal().toLocaleString()}円`);

  // 3. ブラックフライデーセール（20% OFF）
  cart.setStrategy(new PercentageDiscount(20));
  console.log(`ブラックフライデー (20% OFF): ${cart.calculateTotal().toLocaleString()}円`);

  // 4. まとめ買いキャンペーン（5個以上で15% OFF）
  cart.setStrategy(new BulkDiscount(5, 15));
  console.log(`まとめ買い割引 (5個以上で15% OFF): ${cart.calculateTotal().toLocaleString()}円`);

  // 5. 【TSならでは】クラスを作らずアロー関数でその場限りのStrategyを作る
  cart.setStrategy({
    applyDiscount: (items) => {
      // 例: 5,000円超える商品だけ1,000円引きする特別ルール
      const subtotal = items.reduce((sum, item) => sum + getSubtotal(item), 0);
      return subtotal - 1000;
    },
  });
  console.log(`ワンオフ（即席）戦略適用: ${cart.calculateTotal().toLocaleString()}円`);
}

main();