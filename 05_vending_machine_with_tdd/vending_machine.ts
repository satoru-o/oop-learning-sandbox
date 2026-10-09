import { Payment } from "./payment";

export class VendingMachine {
  private payment = new Payment();

  get balance() {
    return this.payment.balance;
  }

  insertMoney(money: number) {
    this.payment.insert(money);
  }
}

