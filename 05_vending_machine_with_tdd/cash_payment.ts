import type { PaymentMethod } from "./payment_method";

const VALID_CASH_VALUES = [10, 50, 100, 500, 1000] as const;

export class CashPayment implements PaymentMethod {
  private _balance: number = 0;

  get balance(): number {
    return this._balance;
  }

  insert(money: number): void {
    const isValid = (VALID_CASH_VALUES as readonly number[]).includes(money);

    if (!isValid) {
      throw new Error(`[Error] ${money}円は受け付けらない金額です`)
    }
    this._balance += money;
  }

  canPay(price: number): boolean {
    return this._balance >= price;
  }

  changeFor(price: number): number {
    return this._balance - price;
  }

  pay(price: number): number {
    if (price > this._balance) {
      throw new Error(`[Error] 残高不足です`)
    }
    this._balance -= price;
    return this._balance;
  }

  refund(): number {
    const refunded = this._balance;
    this._balance = 0;

    return refunded
  }
}