import { it, expect } from "vitest";
import { SalesLedger } from "../src/sales_ledger";

it("最初は売上が0であること", () => {
  const ledger = new SalesLedger();
  expect(ledger.countOf("お茶")).toBe(0);
  expect(ledger.amountOf("お茶")).toBe(0);
  expect(ledger.totalAmount).toBe(0);
});

it("商品別の販売数と金額を集計できること", () => {
  const ledger = new SalesLedger();
  ledger.record("お茶", 120);
  ledger.record("お茶", 120);
  ledger.record("コーラ", 150);
  expect(ledger.countOf("お茶")).toBe(2);
  expect(ledger.amountOf("お茶")).toBe(240);
  expect(ledger.countOf("コーラ")).toBe(1);
  expect(ledger.totalAmount).toBe(390);
});
