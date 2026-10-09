import type { PaymentMethod } from "./payment_method";

export class ICCardPayment implements PaymentMethod {
  private _balance: number;

  constructor(balance: number) {
    this._balance = balance;
  }

  get balance(): number {
    return this._balance;
  }

  insert(_money: number): void {
    throw new Error(`[Error] ICカードには現金を投入できません`);
  }

  canPay(price: number): boolean {
    return this._balance >= price;
  }

  // ICカードは釣り銭が出ない（ちょうどの額を引き落とす）
  changeFor(_price: number): number {
    return 0;
  }

  pay(price: number): number {
    if (!this.canPay(price)) {
      throw new Error(`[Error] 残高不足です`);
    }
    this._balance -= price;
    return this._balance;
  }

  // 現金を預かっていないので返すものはない。残高はカードに残る
  refund(): number {
    return 0;
  }
}
