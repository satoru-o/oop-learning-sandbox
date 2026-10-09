import { it, expect } from "vitest";
import { Payment } from "./payment";

it("初期状態では残高が0円であること", () => {
  const payment = new Payment();
  expect(payment.balance).toBe(0);
});

it("お金を投入すると残高が増えること", () => {
  const payment = new Payment();
  payment.insert(100);
  expect(payment.balance).toBe(100);
});

it("存在しない金額(7円)は投入できないこと", () => {
  const payment = new Payment();
  expect(() => payment.insert(7)).toThrow();
});

it("価格以上の残高なら釣り銭額を返すこと", () => {
  const payment = new Payment();
  payment.insert(500);
  const change = payment.pay(120);
  expect(change).toBe(380);
});

it("残高が足りないと例外になること", () => {
  const payment = new Payment();
  payment.insert(100);
  expect(() => payment.pay(120)).toThrow();
});

it("払い戻しすると残高が0になり、返す金額を得ること", () => {
  const payment = new Payment();
  payment.insert(500);
  const refunded = payment.refund();
  expect(refunded).toBe(500);
  expect(payment.balance).toBe(0);
});