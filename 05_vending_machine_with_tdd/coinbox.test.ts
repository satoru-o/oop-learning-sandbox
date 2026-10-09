import { it, expect } from "vitest";
import { CoinBox } from "./coinbox";

it("硬貨の枚数を持つこと", () => {
  const box = new CoinBox({ 100: 5, 10: 3 });
  expect(box.count(100)).toBe(5);
  expect(box.count(10)).toBe(3);
});

it("380円を大きい硬貨から払い出すこと", () => {
  const box = new CoinBox({ 100: 5, 50: 5, 10: 5 });
  expect(box.payOut(380)).toEqual({ 100: 3, 50: 1, 10: 3 });
});

it("払い出せないときは例外になること", () => {
  const box = new CoinBox({ 100: 1 });
  expect(() => box.payOut(30)).toThrow("[Error] 釣り銭を払い出せません");
});