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
    this._stock -= 1;
  }
}