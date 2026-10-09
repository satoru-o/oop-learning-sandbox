export class CoinBox {
  private _coins: Record<number, number>;

  constructor(coins: Record<number, number>) {
    this._coins = { ...coins };
  }

  count(value: number): number {
    return this._coins[value] ?? 0;
  }

  payOut(amount: number): Record<number, number> {
    const result: Record<number, number> = {};
    let rest = amount;

    for (const value of [1000, 500, 100, 50, 10]) {
      const use = Math.min(Math.floor(rest / value), this.count(value));
      if (use > 0) {
        result[value] = use;
        rest -= value * use;
      }
    }

    if (rest > 0) {
      throw new Error(`[Error] 釣り銭を払い出せません`)
    }

    for (const [value, use] of Object.entries(result)) {
      this._coins[Number(value)] -= use;
    }
    return result;
  }

}