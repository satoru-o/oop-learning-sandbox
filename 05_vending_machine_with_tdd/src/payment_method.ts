// 支払い方法の共通の約束。VendingMachine は現金かICカードかを知らずに使う
export interface PaymentMethod {
  readonly balance: number;
  // 現金の投入（受け付けない方法は例外にする）
  insert(money: number): void;
  canPay(price: number): boolean;
  // 硬貨で返す釣り銭の額
  changeFor(price: number): number;
  // 支払いを確定し、支払い後の残高を返す
  pay(price: number): number;
  // 利用者に返す金額（返すものがなければ 0）
  refund(): number;
}
