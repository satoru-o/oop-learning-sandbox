import { Product } from "./product";

export class Slot {
  private _stock: number
  constructor(
    readonly product: Product,
    stock: number,
  ) {
    this._stock = stock;
  }

  get stock(): number {
    return this._stock
  }

  dispense(): void {
    const currentStock = this._stock;

    if (currentStock <= 0) {
      throw new Error(`[Error] 在庫切れです`)
    }

    this._stock -= 1;
  }
}