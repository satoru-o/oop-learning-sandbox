import { describe, it, expect } from "vitest";
import { VendingMachine } from "./vending_machine";
import { Slot } from "./slot";
import { Product } from "./product";
import { CoinBox } from "./coinbox";
import { ICCardPayment } from "./ic_card_payment";

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

describe("VendingMachine.buy", () => {
  const setup = (stock = 5, coins: Record<number, number> = { 100: 5, 50: 5, 10: 5 }) => {
    const slot = new Slot(new Product("お茶", 120), stock);
    const coinBox = new CoinBox(coins);
    const machine = new VendingMachine([slot], coinBox);
    return { machine, slot, coinBox };
  };

  it("購入すると釣り銭を返し、在庫と残高が減ること", () => {
    const { machine, slot } = setup();
    machine.insertMoney(500);
    const change = machine.buy("お茶");
    expect(change).toEqual({ 100: 3, 50: 1, 10: 3 });
    expect(slot.stock).toBe(4);
    expect(machine.balance).toBe(0);
  });

  it("釣り銭に使った硬貨は釣り銭箱から減ること", () => {
    const { machine, coinBox } = setup();
    machine.insertMoney(500);
    machine.buy("お茶");
    expect(coinBox.count(100)).toBe(2);
  });

  it("残高が足りないと購入できず、在庫は減らないこと", () => {
    const { machine, slot } = setup();
    machine.insertMoney(100);
    expect(() => machine.buy("お茶")).toThrow("残高不足");
    expect(slot.stock).toBe(5);
    expect(machine.balance).toBe(100);
  });

  it("在庫切れだと購入できず、残高は減らないこと", () => {
    const { machine } = setup(0);
    machine.insertMoney(500);
    expect(() => machine.buy("お茶")).toThrow("在庫切れ");
    expect(machine.balance).toBe(500);
  });

  it("釣り銭を払い出せないと購入できず、在庫も残高も変わらないこと", () => {
    const { machine, slot } = setup(5, { 100: 1 });
    machine.insertMoney(500);
    expect(() => machine.buy("お茶")).toThrow("釣り銭を払い出せません");
    expect(slot.stock).toBe(5);
    expect(machine.balance).toBe(500);
  });

  it("存在しない商品は購入できないこと", () => {
    const { machine } = setup();
    machine.insertMoney(500);
    expect(() => machine.buy("コーラ")).toThrow("商品がありません");
  });

  it("払い戻しすると投入した金額が戻り、残高が0になること", () => {
    const { machine } = setup();
    machine.insertMoney(500);
    expect(machine.refund()).toBe(500);
    expect(machine.balance).toBe(0);
  });
});

describe("VendingMachine（ICカード払い）", () => {
  it("釣り銭箱が空でも購入でき、カードの残高から引き落とされること", () => {
    const slot = new Slot(new Product("お茶", 120), 5);
    const card = new ICCardPayment(1000);
    const machine = new VendingMachine([slot], new CoinBox({}), card);
    expect(machine.buy("お茶")).toEqual({});
    expect(card.balance).toBe(880);
    expect(slot.stock).toBe(4);
  });

  it("カードの残高が足りないと購入できず、在庫もカードも変わらないこと", () => {
    const slot = new Slot(new Product("お茶", 120), 5);
    const card = new ICCardPayment(100);
    const machine = new VendingMachine([slot], new CoinBox({}), card);
    expect(() => machine.buy("お茶")).toThrow("残高不足");
    expect(slot.stock).toBe(5);
    expect(card.balance).toBe(100);
  });
});

describe("VendingMachine（売上集計）", () => {
  it("購入に成功すると売上に記録されること", () => {
    const machine = new VendingMachine([new Slot(new Product("お茶", 120), 5)], new CoinBox({ 100: 5, 50: 5, 10: 5 }));
    machine.insertMoney(500);
    machine.buy("お茶");
    expect(machine.sales.countOf("お茶")).toBe(1);
    expect(machine.sales.totalAmount).toBe(120);
  });

  it("購入に失敗したときは売上に記録されないこと", () => {
    const machine = new VendingMachine([new Slot(new Product("お茶", 120), 5)], new CoinBox({}));
    machine.insertMoney(100);
    expect(() => machine.buy("お茶")).toThrow();
    expect(machine.sales.totalAmount).toBe(0);
  });
});
