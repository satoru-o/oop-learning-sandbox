import { it, expect } from "vitest";
import { Product } from "./product";

it("商品は名前と価格を持つこと", () => {
  const tea = new Product("お茶", 120);
  expect(tea.name).toBe("お茶")
  expect(tea.price).toBe(120);
})