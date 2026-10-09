import { it, expect } from "vitest";
import { ICCardPayment } from "../src/ic_card_payment";

it("カードの残高を持つこと", () => {
  expect(new ICCardPayment(1000).balance).toBe(1000);
});

it("残高が価格以上なら払えること", () => {
  const card = new ICCardPayment(120);
  expect(card.canPay(120)).toBe(true);
  expect(card.canPay(121)).toBe(false);
});

it("ICカードは釣り銭が出ないこと", () => {
  expect(new ICCardPayment(1000).changeFor(120)).toBe(0);
});

it("支払うとカードの残高から引き落とされること", () => {
  const card = new ICCardPayment(1000);
  card.pay(120);
  expect(card.balance).toBe(880);
});

it("残高が足りないと支払えないこと", () => {
  const card = new ICCardPayment(100);
  expect(() => card.pay(120)).toThrow("残高不足");
});

it("払い戻しでは何も返らず、カードの残高はそのままであること", () => {
  const card = new ICCardPayment(1000);
  expect(card.refund()).toBe(0);
  expect(card.balance).toBe(1000);
});

it("ICカードには現金を投入できないこと", () => {
  expect(() => new ICCardPayment(1000).insert(100)).toThrow("現金");
});
