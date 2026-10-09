import { Product } from "./product";

export class Slot {
  private _product: Product;
  private _stock: number
  constructor(
    readonly product: Product,
    stock: number,
  ) {
    this._product = product;
    this._stock = stock;
  }

  get stock(): number {
    return this._stock
  }

  dispense(): void {
    this._stock -= 1;
  }
}