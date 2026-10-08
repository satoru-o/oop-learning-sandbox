import { describe, it, expect } from "vitest";
import { VendingMachine } from "./vending_machine";

describe("VendingMachine", () => {
  it("初期状態では残高が0円であること", () => {
    const machine = new VendingMachine();
    expect(machine.balance).toBe(0)
  });

  it("お金を投入すると残高が増加すること", () => {
    const machine = new VendingMachine();
    machine.insertMoney(100);
    expect(machine.balance).toBe(100);
  })

  it("存在しない金額(7円)は投入できないこと", () => {
    const machine = new VendingMachine();
    expect(() => machine.insertMoney(7)).toThrow();
  });
})
