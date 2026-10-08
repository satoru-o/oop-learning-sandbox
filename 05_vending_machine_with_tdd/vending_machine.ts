const VALID_CASH_VALUES = [10, 50, 100, 500, 1000] as const;

export class VendingMachine {
  private _balance: number;

  constructor(initialBalance: number = 0) {
    this._balance = initialBalance;
  }

  get balance() {
    return this._balance;
  }

  insertMoney(money: number): void {
    const isValid = (VALID_CASH_VALUES as readonly number[]).includes(money);

    if (!isValid) {
      throw new Error(`[Error] ${money}円は受け付けらない金額です`)
    }

    this._balance += money;
  }
}

