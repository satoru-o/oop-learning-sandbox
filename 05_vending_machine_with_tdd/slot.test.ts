import { it, expect } from "vitest";
import { Product } from "./product";
import { Slot } from "./slot";

it("列は商品と在庫を持つこと", () => {
  const slot = new Slot(new Product("お茶", 120), 5);
  expect(slot.product.name).toBe("お茶");
  expect(slot.stock).toBe(5);
});
