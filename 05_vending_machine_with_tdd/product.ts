export class Product {
  private _name: string;
  private _price: number;

  constructor(
    readonly productName: string,
    readonly productPrice: number,
  ) {
    this._name = productName;
    this._price = productPrice;
  }

  get name(): string {
    return this._name;
  }

  get price(): number {
    return this._price;
  }
}