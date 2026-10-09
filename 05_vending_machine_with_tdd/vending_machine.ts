import { CoinBox } from "./coinbox";
import { CashPayment } from "./cash_payment";
import type { PaymentMethod } from "./payment_method";
import { Slot } from "./slot";

export class VendingMachine {
  constructor(
    private slots: Slot[] = [],
    private coinBox: CoinBox = new CoinBox({}),
    private payment: PaymentMethod = new CashPayment(),
  ) {}

  get balance() {
    return this.payment.balance;
  }

  insertMoney(money: number) {
    this.payment.insert(money);
  }

  // 全部のチェックを通してから状態を変える（途中で失敗しても何も変わらない）
  buy(productName: string): Record<number, number> {
    const slot = this.slots.find((s) => s.product.name === productName);
    if (!slot) {
      throw new Error(`[Error] 商品がありません: ${productName}`);
    }
    if (!slot.hasStock) {
      throw new Error(`[Error] ${productName}は在庫切れです`);
    }
    const price = slot.product.price;
    if (!this.payment.canPay(price)) {
      throw new Error(`[Error] 残高不足です`);
    }

    const change = this.coinBox.payOut(this.payment.changeFor(price));

    this.payment.pay(price);
    this.payment.refund();
    slot.dispense();
    return change;
  }

  refund(): number {
    return this.payment.refund();
  }
}
