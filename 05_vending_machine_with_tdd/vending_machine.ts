export class VendingMachine {
  private _balance: number;

  constructor(initialBalance: number = 0) {
    this._balance = initialBalance;
  }

  get balance() {
    return this._balance;
  }

  insertMoney(money: number): number {
    this._balance += money
    return this._balance
  }
}