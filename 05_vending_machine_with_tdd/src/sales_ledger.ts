export class SalesLedger {
  private _sales = new Map<string, { count: number; amount: number }>();

  record(productName: string, price: number): void {
    const current = this._sales.get(productName) ?? { count: 0, amount: 0 };
    this._sales.set(productName, {
      count: current.count + 1,
      amount: current.amount + price,
    });
  }

  countOf(productName: string): number {
    return this._sales.get(productName)?.count ?? 0;
  }

  amountOf(productName: string): number {
    return this._sales.get(productName)?.amount ?? 0;
  }

  get totalAmount(): number {
    let total = 0;
    for (const { amount } of this._sales.values()) {
      total += amount;
    }
    return total;
  }
}
