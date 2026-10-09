import { it, expect } from "vitest";
import { Product } from "../src/product";
import { Slot } from "../src/slot";

it("列は商品と在庫を持つこと", () => {
  const slot = new Slot(new Product("お茶", 120), 5);
  expect(slot.product.name).toBe("お茶");
  expect(slot.stock).toBe(5);
});

it("1本取り出すと在庫が1減ること", () => {
  const slot = new Slot(new Product("お茶", 120), 5);
  slot.dispense();
  expect(slot.stock).toBe(4);
});

it("在庫が0のとき取り出すと例外になること", () => {
  const slot = new Slot(new Product("お茶", 120), 0);
  expect(() => slot.dispense()).toThrow();
});
